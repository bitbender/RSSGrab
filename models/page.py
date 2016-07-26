class Page:

    def __init__(self, url, html, isPayed = False):
        self.url = url
        self.isPayed = isPayed
        self.html = html

    def __repr__(self):
        return self.url

    def toDoc(self):
        return self.__dict__
