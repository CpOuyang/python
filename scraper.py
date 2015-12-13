from urllib.request import urlopen
from bs4 import BeautifulSoup
import re


class Page:
    """"""
    def __init__(self, url):
        assert isinstance(url, str)
        self._url = url if re.match(r"^http", url.lower()) else "http://" + re.sub(r"/*", r"", url.lower())
        self._trials = ("utf8", "cp950", "ascii", "latin1")

        # Bind together
        self._source = ""
        self._encoding = ""

    def _get_source(self):
        """-> str"""
        try:
            html = urlopen(self._url)
            content = html.read()
            for encoding in self._trials:
                try:
                    a = content.decode(encoding)
                    self._source, self._encoding = a, encoding
                    return a
                except:
                    pass
        except:
            print("invalid url or bad connection")


    @property
    def encoding(self):
        if self._encoding:
            return self._encoding
        else:
            self._get_source()
            return self._encoding

    @property
    def source(self):
        if self._source:
            return self._source
        else:
            self._get_source()
            return self._source

    @property
    def tags(self):
        ans = set()
        for tag in BeautifulSoup(self.source, "html.parser").find_all():
            ans.add(tag.name)
        return ans

    @property
    def urls(self, lv=1):
        ans = list()
        for tag in self.tags:
            for element in BeautifulSoup(self.source, "html.parser").find_all(tag):
                # print(element.name + " -> " + element.attrs.__repr__())
                print(element.name + " -> " + list(element.children).__repr__())


target = "http://tw.yahoo.com/"

p = Page(target)

print(p.source)
