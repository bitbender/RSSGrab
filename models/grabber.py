from bson import ObjectId
import copy
import feedparser
import logging
import requests
from time import mktime
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from datetime import datetime as dt


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

    def __init__(self, name, feed, interval, css_selector=None, _id=None):

        if type(_id) == str:
            self._id = ObjectId(_id)

        elif type(_id) == ObjectId:
            self._id = _id

        else:
            self._id = ObjectId()

        self.name = name
        self.feed = feed
        self.css_selector = css_selector
        self.interval = interval

    def run(self):
        """
        This method starts the parsing of the feed.
        """
        data = feedparser.parse(self.feed)
        # check here to see data format
        for rss_item in data['entries']:
            self.store_rss_item(rss_item)

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
        response = requests.get(url)

        if response.status_code == 200:
            result.append(response.text)

            if self.css_selector:
                soup = BeautifulSoup(response.text, 'html.parser')

                pages = [page['href'] for page in soup.select(self.css_selector)]
                for page in pages:
                    next_page = requests.get(parsed_url.scheme+'://'+parsed_url.netloc+'/'+page)

                    if next_page.status_code == 200:
                        result.append(next_page.text)

        return result

        #response.raise_for_status()

    def save(self):
        """
        Save the grabber to a mongodb database.

        :return: the document id of the grabber in the database.
        """
        connection = SmplConnPool.get_instance().get_connection()
        grabber_collection = connection[
            Grabber.cfg['database']['db']]['grabbers']
        grabber_id = grabber_collection.insert_one(self.__dict__).inserted_id
        logging.info('Saved grabber with id {}'.format(grabber_id))
        # self._id = ObjectId(grabber_id)
        return grabber_id

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
        article_url = rss_item['link']

        # convert time.struct_time to datetime.datetime
        rss_item['published'] = dt.fromtimestamp(mktime(rss_item['published_parsed']))
        del rss_item['published_parsed']

        # download the article referred to the rss feed
        rss_item['articles'] = self._download_website(article_url)

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
    def decode(doc):
        """
        Takes a document / dictionary and reconstructs a Grabber from the
        given information.
        :param doc: the document containing the Grabber specification
        :return: a new instance of a Grabber
        """
        assert type(doc) == dict
        # TODO: A builder pattern would certainly be the better choice here.
        if '_id' in doc and 'css_selector' in doc:
            return Grabber(name=doc['name'], feed=doc['feed'], interval=doc['interval'], css_selector=doc['css_selector'], _id=doc['_id'])
        elif '_id' in doc and not 'css_selector' in doc:
            return Grabber(name=doc['name'], feed=doc['feed'], interval=doc['interval'], _id=doc['_id'])
        elif '_id' not in doc and 'css_selector' in doc:
            return Grabber(name=doc['name'], feed=doc['feed'], interval=doc['interval'], css_selector=doc['css_selector'])
        else:
            return Grabber(doc['name'], doc['feed'], doc['interval'])

    def __repr__(self):
        return '[{0}, {1}, {2}, {3}]'.format(self._id, self.name, self.feed, self.interval)
