from bs4 import BeautifulSoup
from urllib.parse import urlparse
from urllib.request import urlopen
import re


class Page:
    """Dunno what to write yet"""
    def __init__(self, url):
        assert isinstance(url, str)
        # url prefix
        self._url = url.lower().strip() if re.match(r"^http", url.lower().strip())\
            else "http://" + re.sub(r"/*", r"", url.lower().strip())
        # url parsing
        self._urlparse = urlparse(self._url)
        # encoding checking priority
        self._trials = ("utf8", "cp950", "ascii", "latin1")

        # Bind together in action
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
    def tag_names(self):
        ans = set()
        for tag in BeautifulSoup(self.source, "html.parser").find_all():
            ans.add(tag.name)
        return ans

    @property
    def domain_name(self):
        return self._urlparse.scheme + "://" + self._urlparse.netloc + "/"

    @property
    def links(self, lv=1):
        ans = list()
        for tag_name in self.tag_names:
            for tag in BeautifulSoup(self.source, "html.parser").find_all(tag_name):
                try:
                    for attr in ("href", "action"):
                        link = tag[attr].lower().strip()
                        link = re.sub(r"^//", self._urlparse.scheme + "://", link)
                        link = re.sub(r"^/", self._urlparse.scheme + "://" + self._urlparse.netloc + "/", link)
                        # unless ...
                        if not re.findall(r"^javascript:|\.(png|ico)$", link):
                            ans.append(link)
                except:
                    pass
        return ans


target = "www.wikipedia.org"

p = Page(target)

print(p.source, "\r")

for a in sorted(p.links): print(a)
