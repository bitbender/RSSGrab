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

logger = logging.getLogger('server')


class Grabber:
    cfg = Config.get_instance()

    # keeps track of the urls that have been
    # downloaded already
    crawl_state = set()

    # temporarily stores the statistics of one grabber run
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
        self.createdAt = self.lastModified = dt.utcnow()
        self.lastRun = None
        self.status = 'suspended'

    def run(self):
        """
        This method starts the parsing of the feed.
        """
        Grabber.stats = Statistic(self._id)
        Grabber.stats.start_time = dt.utcnow()
        self.lastRun = dt.utcnow()

        logger.info('{0}: Starting the crawl'.format(self._id))
        self.status = 'running'

        data = feedparser.parse(self.feed)
        # check here to see data format
        for rss_item in data['entries']:
            self.store_rss_item(rss_item)

        logger.info('{0}: Finished'.format(self._id))

        Grabber.stats.end_time = dt.utcnow()
        Grabber.stats.save()
        Grabber.stats = None

        # call save in order to persist the lastRun
        self.save()
        self.status = 'scheduled'


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
        Grabber.crawl_state.add(url)

        if response.status_code == 200:

            soup = BeautifulSoup(response.text, 'html.parser')

            # Check website for payed content
            if self.payed_selector:

                if len(soup.select(self.payed_selector)) > 0:
                    result.append(Page(url, response.text, True))
                    Grabber.stats.payed.append(url)
                else:
                    result.append(Page(url, response.text, False))
            else:
                result.append(Page(url, response.text, False))

            # apply the pagination css selector only to free sites
            if not result[0].isPayed and self.css_selector:
                pages = self._paginate(url_prefix, response, self.css_selector, result)
                Grabber.crawl_state = set()
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
                if page.startswith(url_prefix):
                    url = page
                else:
                    url = url_prefix + page

                if url not in Grabber.crawl_state:
                    Grabber.crawl_state.add(url)
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
        grabber_collection = connection[Grabber.cfg['database']['db']]['grabbers']

        # let lastModified timestamp
        self.lastModified = dt.utcnow()

        # remove elements that should not be saved
        to_be_saved = self.encode(['status'])

        result = grabber_collection.update_one(
            {'_id': self._id},
            {'$set': to_be_saved},
            True
        )

        return result.upserted_id

    def delete(self):
        """
        Delete the grabber from the mongodb database.

        :return: the document id of the grabber in the database.
        """
        connection = SmplConnPool.get_instance().get_connection()
        grabber_collection = connection[Grabber.cfg['database']['db']]['grabbers']

        result = grabber_collection.delete_one({'_id': self._id})

        return result.deleted_count

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

        # only try to download something if the rss element contains a valid article link.
        if 'link' in rss_item:
            article_url = rss_item['link']

            # convert time.struct_time to datetime.datetime
            if 'published_parsed' in rss_item:
                rss_item['published'] = dt.fromtimestamp(mktime(rss_item['published_parsed']))
                del rss_item['published_parsed']

            # download the article referred to the rss feed
            # note that one articles can consist of multiple pages
            rss_item['articles'] = [page.toDoc() for page in self._download_website(article_url)]
            Grabber.stats.total_pages += len(rss_item['articles'])

            connection = SmplConnPool.get_instance().get_connection()
            feed_collection = connection[Grabber.cfg['database']['db']][
                Grabber.cfg['database']['collections']['articles']]

            if 'id' not in rss_item or rss_item['id'] == '':
                rss_item['id'] = rss_item['link']

            # try to fetch the article from database
            db_feed = feed_collection.find({'id': rss_item['id']})

            assert db_feed.count() < 2, "id should be a primary key"
            if not db_feed.count() > 0:
                feed_collection.save(rss_item)
                Grabber.stats.new.append(article_url)
            else:
                self.update_feed(db_feed[0], rss_item)

    def update_feed(self, old_rss_item, new_rss_item):
        """
        Replaces old rss item with the new one.
        :param old_rss_item:
        :param new_rss_item:
        :return:
        """
        assert old_rss_item['id'] == new_rss_item['id'], 'Updates should only \
                be made to a newer version of the article'

        # get connection to the feed collection
        connection = SmplConnPool.get_instance().get_connection()
        feed_collection = connection[Grabber.cfg['database']['db']][
            Grabber.cfg['database']['collections']['articles']]

        if 'published' in old_rss_item:
            # check if the new feed is really newer then the old one
            if old_rss_item['published'] < new_rss_item['published']:

                # replace the old article with the newer one
                feed_collection.replace_one({'id': new_rss_item['id']}, new_rss_item)
                Grabber.stats.updated.append(new_rss_item['link'])
        else:
            # if no published field exists, always replace the old item with the new one.
            feed_collection.replace_one({'id': new_rss_item['id']}, new_rss_item)

    def encode(self, rm=None):
        """
        Encode the grabber as a dictionary

        :param rm: the fields of the grabber that should me excluded from serialization
        :return: a dictionary encoding of the grabber
        """

        if rm is None:
            rm = []
        else:
            rm.extend([])

        # Copy the dictionary with all attributes of this object.
        result = copy.deepcopy(self.__dict__)

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
        if 'lastModified' in doc:
            grabber.lastModified = doc['lastModified']
        if 'lastRun' in doc:
            grabber.lastRun = doc['lastRun']

        return grabber

    def __repr__(self):
        return '[{0}, {1}, {2}, {3}]'.format(self._id, self.name, self.feed, self.interval)
