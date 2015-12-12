from urllib.request import urlopen
from bs4 import BeautifulSoup
import re


class Page:
    def __init__(self, url):
        assert isinstance(url, str)
        self._url = url if re.match(r"^http", url.lower()) else "http://" + re.sub(r"/*", r"", url.lower())

    def guess_encoding(self, encodings=("utf8", "cp950", "ascii"), dept=10240):
        html = urlopen(self._url)
        content = html.read(dept)
        # a = b""
        # (lambda a, b: a + c for c in b)(b"", )
        for encoding in encodings:
            try:
                content.decode(encoding)
            except Exception as error:
                print(error)
            else:
                print(content)
                return encoding

    @property
    def source(self):
        """-> str"""
        html = urlopen(self._url)
        try:
            content = html.read()
            return content.decode(self.guess_encoding())
        except Exception as error:
            print(error)

    @property
    def tag_name(self, lv=1):
        return self.source(self._url).__class__

target = "http://www.mobile01.com/"

p = Page(target)

a = ""
print((lambda: a + "b")())
