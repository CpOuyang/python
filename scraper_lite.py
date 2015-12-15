from bs4 import BeautifulSoup
from urllib.parse import urlparse, quote
from urllib.request import urlopen, urlretrieve, url2pathname
import os, re, time


class Page:
    """Dunno what to write yet"""
    # to be solved: 1.short url
    def __init__(self, url, method="static"):
        """type = {"static", "dynamic"}"""
        assert isinstance(url, str)
        # url prefix
        self._url = url.lower().strip() if re.findall(r"^http", url.lower().strip())\
            else "http://" + re.sub(r"^/*", r"", url.lower().strip())
        # url parsing
        self._urlparse = urlparse(self._url)
        # encoding checking priority
        self._trials = ("utf8", "cp950", "ascii", "latin1")

        # Bind together in action
        self._source = ""
        self._encoding = ""

        assert method.lower() in ("static", "dynamic", "s", "d")
        self._method = "static" if method.lower() in ("static", "s") else "dynamic"

    def _get_source(self):
        """-> str"""
        try:
            if self._method == "static":
                html = urlopen(self._url)
                content = html.read()
                for encoding in self._trials:
                    try:
                        a = content.decode(encoding)
                        self._source, self._encoding = a, encoding
                        return a
                    except:
                        pass
            elif self._method == "dynamic":
                from selenium import webdriver
                import time

                browser = webdriver.Firefox()
                browser.get(self._url)
                time.sleep(5)
                self._source, self._encoding = browser.page_source, None
                browser.close()
                return self._source
        except:
            print("invalid url or bad connection: %s" % self._url)

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
    def links(self):
        ans = list()
        for tag_name in self.tag_names:
            for tag in BeautifulSoup(self.source, "html.parser").find_all(tag_name):
                for attr in ("href", "action", "src"):
                    if tag.has_attr(attr):
                        link = tag[attr].lower().strip()
                        link = re.sub(r"^//", self._urlparse.scheme + "://", link)
                        link = re.sub(r"^/", self._urlparse.scheme + "://" + self._urlparse.netloc + "/", link)
                        # unless ...
                        if all([re.search(r"^(#|telnet:|ftp:|data:|javascript:|mailto:)", link) is None,
                                re.search(r"\.(gif|ico|png|jpg)$", link) is None,
                                link]):
                            if not link.startswith("http"):
                                p = self._urlparse
                                if link.endswith((".php", ".js", ".htm", ".html", "css", "asp")):
                                    link = p.scheme + "://" + p.netloc + "/" + link
                                elif urlparse(link).query:
                                    link = p.scheme + "://" + p.netloc + "/" + link
                                elif 2 <= len(link.split("/")):
                                    link = p.scheme + "://" + p.netloc + "/" + link
                                elif 2 <= len(link.split("\.")):
                                    link = p.scheme + "://" + link
                            ans.append(re.sub(r"/$", r"", link))
        return ans


if __name__ == "__main__":

    root = "d:\\scraper"
    sites = {
        "Mobile01": {
            "_home_": "www.mobile01.com",
            "bike": "www.mobile01.com/category.php?id=8",
        },
    }
    # sites = {
    #     "Mobile01": "www.mobile01.com/category.php?id=8",
    #     # "Yahoo News": "tw.news.yahoo.com",
    # }

    # for project in sites:
    #     # path setting
    #     if not os.path.exists(os.path.join(root, project)):
    #         os.makedirs(os.path.join(root, project))
    #     os.environ["TZ"] = "PDT+8PDT"
    #     folder = os.path.join(root, project,
    #                           "_".join([time.strftime("%Y%m%d", time.localtime()),
    #                                     time.strftime("%H%M%S", time.localtime())]))
    #     if not os.path.exists(folder):
    #         os.makedirs(folder)
    #
    #     # scrape
    #     page = Page(sites[project])
    #
    #     if page.source:
    #         with open(os.path.join(folder, "index.html"), "wb+") as f:
    #             f.write(page.source.encode())

    print(url2pathname("www.mobile01.com/category.php?id=8"))



    # NOT working in static way
    target = "www.sinyi.com.tw"
    target = "www.yungching.com.tw"
    target = "www.ctbcbank.com/CTCBPortalWeb/appmanager/ebank/rb"
    target = "www.landbank.com.tw"

    target = "www.appledaily.com.tw"
    target = "www.cnyes.com"
    target = "www.mobile01.com"
    # target = "www.twse.com.tw"
    target = "www.ptt.cc"
    # target = "www.master1995.com.tw"
    # target = "www.etwarm.com.tw"
    # target = "www.wearn.com"

    target = "tw.news.yahoo.com"
    target = "www.mobile01.com/category.php?id=8"

    # p = Page(target)
    #
    # print(p.source)

    # for a in p.links: print(a)

    # print(quote("http://www.google.com/?id=中文"))

    # with open("d:\\zzz\\1.htm", "wb+") as f:
    #     f.write("test".encode())
