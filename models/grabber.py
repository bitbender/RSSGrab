from bson import ObjectId, json_util
import copy
import feedparser
import logging
import requests
from time import mktime
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from datetime import datetime as dt
from models.page import Page
from models.stat import Statistic
import json


from config import Config
from smpl_conn_pool import SmplConnPool

"""
This class represents a grabber. It is responsible for
storing all the information needed in order to grab the
data from the specified rss feed.

Additionally it implements the entire logic of a specific
grab. That means downloading the source code of the articles
in an rss feed
"""


class Grabber:
    cfg = Config.get_instance()

    state = set()
    stats = None

    def __init__(self, name, feed, interval=1800, css_selector=None, payed_selector=None, _id=None):

        if type(_id) == str:
            self._id = ObjectId(_id)

        elif type(_id) == ObjectId:
            self._id = _id

        else:
            self._id = ObjectId()

        self.name = name
        self.feed = feed
        self.css_selector = css_selector
        self.payed_selector = payed_selector
        self.interval = interval
        self.createdAt = dt.utcnow()

    def run(self):
        """
        This method starts the parsing of the feed.
        """
        Grabber.stats = Statistic(self._id)
        Grabber.stats.start_time = dt.utcnow()

        data = feedparser.parse(self.feed)
        # check here to see data format
        for rss_item in data['entries']:
            self.store_rss_item(rss_item)

        Grabber.stats.end_time = dt.utcnow()
        Grabber.stats.save()

    def _download_website(self, url):
        """
        Downloads the website that can be found at the given url. Should
        a css selector be provided, it will use the selector to paginate
        through all the websites that the selector will extract.

        :param url: the website of the url that should be downloaded
        :return: the text downloaded from the url or raise an error instead
        """
        result = []

        parsed_url = urlparse(url)
        url_prefix = parsed_url.scheme + '://' + parsed_url.netloc
        response = requests.get(url)
        Grabber.state.add(url)

        if response.status_code == 200:

            soup = BeautifulSoup(response.text, 'html.parser')

            # Check website for payed content
            if self.payed_selector:
                if len(soup.select(self.payed_selector)) > 0:
                    result.append(Page(url, response.text, True))
                else:
                    result.append(Page(url, response.text, False))
            else:
                result.append(Page(url, response.text, False))

            if not result[0].isPayed and self.css_selector:
                pages = self._paginate(url_prefix, response, self.css_selector, result)
                Grabber.state = set()
                return pages
            else:
                return result
                # pages = [page['href'] for page in soup.select(self.css_selector)]
                # for page in pages:
                #     next_page = requests.get(parsed_url.scheme+'://'+parsed_url.netloc+'/'+page)
                #
                #     if next_page.status_code == 200:
                #         result.append(next_page.text)
        else:
            return result

    def _paginate(self, url_prefix, response, selector, result):
        soup = BeautifulSoup(response.text, 'html.parser')
        pages = [page['href'] for page in soup.select(selector)]

        if len(pages) > 0:
            for page in pages:
                url = url_prefix + page

                if url not in Grabber.state:
                    Grabber.state.add(url)
                    response = requests.get(url)
                    result.append(Page(url, response.text, False))
                    result = self._paginate(url_prefix, response, selector, result)


        return result

    def save(self):
        """
        Save the grabber to a mongodb database.

        :return: the document id of the grabber in the database.
        """
        connection = SmplConnPool.get_instance().get_connection()
        grabber_collection = connection[
            Grabber.cfg['database']['db']]['grabbers']

        result = grabber_collection.update_one(
            {'_id': self._id},
            {'$set': self.__dict__},
            True
        )
        logging.info('Saved grabber with id {}'.format(result.upserted_id))

        return result.upserted_id

    @staticmethod
    def load(grb_id):
        """
        Load a grabber from the mongodb database.

        :return: the document id of the grabber to be loaded.
        """
        connection = SmplConnPool.get_instance().get_connection()
        grabber_collection = connection[
            Grabber.cfg['database']['db']]['grabbers']

        result = grabber_collection.find_one({'_id': ObjectId(grb_id)})
        if result:
            return Grabber.new(result)
        else:
            return None

    def store_rss_item(self, rss_item):
        """
        This method takes an rss_item from the rss feed, downloads
        the article the item points to, and checks if the constructed
        rss item is already in the database.

        If the rss item is already in the database, it tries to update it
        if the downloaded version is newer then the stored version. Otherwise
        it simply saves the constructed rss item to the database.

        :param rss_item: the rss item to be processed
        """
        rss_item['grbid'] = self._id
        article_url = rss_item['guid']
        Grabber.stats.urls.append(article_url)

        # convert time.struct_time to datetime.datetime
        rss_item['published'] = dt.fromtimestamp(mktime(rss_item['published_parsed']))
        del rss_item['published_parsed']

        # download the article referred to the rss feed
        rss_item['articles'] = [page.toDoc() for page in self._download_website(article_url)]
        Grabber.stats.total_pages += len(rss_item['articles'])

        connection = SmplConnPool.get_instance().get_connection()
        feed_collection = connection[Grabber.cfg['database']['db']][
            Grabber.cfg['database']['collections']['articles']]

        # try to fetch the article from database
        db_feed = feed_collection.find({'id': rss_item['id']})

        assert db_feed.count() < 2, "id should be a primary key"
        if not db_feed.count() > 0:
            feed_collection.save(rss_item)
        else:
            self.update_feed(db_feed[0], rss_item)

    def update_feed(self, old_feed, new_feed):
        """
        Replaces old feed with new one.
        :param old_feed:
        :param new_feed:
        :return:
        """
        assert old_feed['id'] == new_feed['id'], 'Updates should only \
                be made to a newer version of the article'
        if self._is_newer(old_feed['published'], new_feed['published']):
            connection = SmplConnPool.get_instance().get_connection()
            feed_collection = connection[Grabber.cfg['database']['db']][
                Grabber.cfg['database']['collections']['articles']]
            feed_collection.replace_one({'id': new_feed['id']}, new_feed)

    def _is_newer(self, old_date, new_date):
        """
        Checks if a date is newer then another date
        :param old_date: older date
        :param new_date: newer date
        :return: true if the old date is truly older else false.
        """
        return old_date < new_date

    def encode(self, rm=None):
        """
        Encode the grabber as a dictionary

        :param rm: the fields of the grabber that should me excluded from serialization
        :return: a dictionary encoding of the grabber
        """

        if rm is None:
            rm = []
        else:
            rm = rm.split(',')

        # Copy the dictionary with all attributes of this object.
        result = copy.deepcopy(self.__dict__)
        # Convert the ObjectId into a string
        result['_id'] = str(self._id)

        for key in rm:
            if key in result:
                del result[key]

        return result

    @staticmethod
    def new(doc):
        """
        Takes a document / dictionary and reconstructs a Grabber from the
        given information.
        :param doc: the document containing the Grabber specification
        :return: a new instance of a Grabber
        """
        assert type(doc) == dict

        if 'name' not in doc:
            raise Exception('A grabber needs to have a name!')
        if 'feed' not in doc:
            raise Exception('A grabber needs to have a feed!')

        if '_id' in doc:
            grabber = Grabber(_id=doc['_id'], name=doc['name'], feed=doc['feed'])
        else:
            grabber = Grabber(name=doc['name'], feed=doc['feed'])

        if 'css_selector' in doc:
            grabber.css_selector = doc['css_selector']
        if 'payed_selector' in doc:
            grabber.payed_selector = doc['payed_selector']
        if 'interval' in doc:
            grabber.interval = doc['interval']
        if 'createdAt' in doc:
            grabber.createdAt = doc['createdAt']

        return grabber

    def __repr__(self):
        return '[{0}, {1}, {2}, {3}]'.format(self._id, self.name, self.feed, self.interval)
