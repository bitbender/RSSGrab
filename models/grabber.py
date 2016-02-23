import feedparser
import requests
import time

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

    def __init__(self, name, feed, interval, _id=None):
        self.name = name
        self.feed = feed
        self.interval = interval
        if _id:
            self._id = _id

    def run(self):
        data = feedparser.parse(self.feed)
        for rss_item in data['entries']:
            self.store_rss_item(rss_item)

    def download_article(self, article_url):
        response = requests.get(article_url)
        if response.status_code == 200:
            return response.text

        response.raise_for_status()

    def save(self):
        connection = SmplConnPool.get_instance().get_connection()
        grabber_collection = connection[
            Grabber.cfg['database']['db']]['grabbers']
        grabber_id = grabber_collection.insert_one(self.__dict__).inserted_id
        print('Saved grabber with id {}'.format(grabber_id))
        return grabber_id

    def store_rss_item(self, rss_item):
        article_url = rss_item['link']
        rss_item['article'] = self.download_article(article_url)
        connection = SmplConnPool.get_instance().get_connection()
        feed_collection = connection[Grabber.cfg['database']['db']][
            Grabber.cfg['database']['collections']['articles']]
        db_feed = feed_collection.find({'id': rss_item['id']})
        assert db_feed.count() < 2, "id should be a primary key"
        if not db_feed.count() > 0:
            feed_collection.save(rss_item)
        else:
            self.update_feed(db_feed[0], rss_item)

    def update_feed(self, old_feed, new_feed):
        # Replaces old feed with new one if it is published at another time
        assert old_feed['id'] == new_feed['id'], 'Updates should only \
                be made to a newer version of the article'
        if self.is_newer(old_feed['published'], new_feed['published']):
            connection = SmplConnPool.get_instance().get_connection()
            feed_collection = connection[Grabber.cfg['database']['db']][
                Grabber.cfg['database']['collections']['articles']]
            feed_collection.replace_one({'id': new_feed['id']}, new_feed)

    def is_newer(self, old_date, new_date):
        # Parse date with format Fri, 05 Feb 2016 13:28:12 -0000
        old = time.strptime(old_date.replace(',', ''), '%a %d %b %Y %X %z')
        new = time.strptime(new_date.replace(',', ''), '%a %d %b %Y %X %z')
        return old < new

    def to_json(self):
        return {
            'id': str(self._id),
            'name': self.name,
            'feed': self.feed,
            'interval': self.interval
        }
