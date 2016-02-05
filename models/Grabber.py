import feedparser
import requests

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

    def __init__(self, name, feed, db=('localhost', 27017)):
        self.name = name
        self.feed = feed
        self.db = db
        self.status = 'Inactive'
        self.pagination_selector = None

    def run(self):
        # TODO: The logic on how to extract information from the feed, and
        # on how to download the articles contained within the feed should go
        # here. Use the requests lib to download the articles

        data = feedparser.parse(self.feed)
        for rss_item in data['entries']:
            self.store_rss_item(rss_item)

    def download_article(self, article_url):
        response = requests.get(article_url)
        if response.status_code == 200:
            return response.text

        response.raise_for_status()

    def store_rss_item(self, rss_item):
        article_url = rss_item['link']
        rss_item["article"] = self.download_article(article_url)
        connection = SmplConnPool.get_instance().get_connection()
        feed_collection = connection["local"]["Feeds"]
        if not feed_collection.find({'id': rss_item['id']}).count() > 0:
            feed_collection.save(rss_item)
