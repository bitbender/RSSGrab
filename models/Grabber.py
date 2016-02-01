import feedparser

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
        print([entry['title_detail']['value'] for entry in data['entries']])