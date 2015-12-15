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

    def get_links(self, name=None, attrs={}, text=None, limit=None):
        """name: tags to be looked for
        attrs: dictionary of attributes"""
        ans = list()
        for tag in BeautifulSoup(self.source, "html.parser").find_all(name=name, attrs=attrs, text=text, limit=limit):
            for attr in ("href", "action", "src"):
                if tag.has_attr(attr):
                    # REMARK: href could be case-sensitive (e.g., www.ptt.cc)
                    link = tag[attr]
                    link = re.sub(r"^//", self._urlparse.scheme + "://", link)
                    link = re.sub(r"^/", self._urlparse.scheme + "://" + self._urlparse.netloc + "/", link)
                    # unless ...
                    if all([re.search(r"^(#|telnet:|ftp:|data:|javascript:|mailto:)", link) is None,
                            re.search(r"\.(gif|ico|png|jpg)$", link) is None,
                            link]):
                        if not link.startswith("http"):
                            if link.endswith((".php", ".js", ".htm", ".html", ".css", ".asp")):
                                link = self.domain_name + link
                            elif urlparse(link).query:
                                link = self.domain_name + link
                            elif 2 <= len(link.split("/")):
                                link = self.domain_name + link
                            elif 2 <= len(link.split("\.")):
                                link = self._urlparse.scheme + "://" + link
                        ans.append(re.sub(r"/$", r"", link))
        return ans


if __name__ == "__main__":

    root = "e:\\scraper"
    projs = {
        "Yahoo News Politics": {
            "home": "tw.news.yahoo.com/politics",
            "attrs": {
                "class": "title ",
                "href": re.compile(r"\.html$"),
            },
        },
        "Yahoo News Sports": {
            "home": "tw.news.yahoo.com/sports",
            "attrs": {
                "class": "title ",
                "href": re.compile(r"\.html$"),
            },
        },
        "PTT Creditcard": {
            "home": "www.ptt.cc/bbs/creditcard/index.html",
            "attrs": {
                "href": re.compile(r"M\.\d{10}\."),
            }
        },
    }

    # for proj in projs:
    #     time_stamp = "_".join([time.strftime("%Y%m%d", time.localtime()),
    #                            time.strftime("%H%M%S", time.localtime())])
    #     if not os.path.exists(os.path.join(root, proj, time_stamp)):
    #         os.makedirs(os.path.join(root, proj, time_stamp))
    #
    #     page = Page(projs[proj]["home"])
    #
    #     keys = projs[proj].keys()
    #     links = page.get_links(name=projs[proj]["tags"] if "tags" in keys else None,
    #                            attrs=projs[proj]["attrs"] if "attrs" in keys else {},
    #                            text=projs[proj]["text"] if "text" in keys else None,
    #                            limit=projs[proj]["limit"] if "limit" in keys else None)
    #
    #     print("=" * 20 + "Get links as follows:" + "=" * 20)
    #     for link in links:
    #         print(link)

    # projects = {
    #     "Mobile01": "www.mobile01.com",
    #     "Yahoo News": "tw.news.yahoo.com",
    # }
    #
    # for project in projects:
    #     # path setting
    #     if not os.path.exists(os.path.join(root, project)):
    #         os.makedirs(os.path.join(root, project))
    #     folder = os.path.join(root, project,
    #                           "_".join([time.strftime("%Y%m%d", time.localtime()),
    #                                     time.strftime("%H%M%S", time.localtime())]))
    #     if not os.path.exists(folder):
    #         os.makedirs(folder)
    #
    #     # scrape
    #     page = Page(projects[project])
    #
    #     if page.source:
    #         with open(os.path.join(folder, "index.html"), "wb+") as f:
    #             f.write(page.source.encode())

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
    target = r"tw.news.yahoo.com/politics"
    # target = "www.mobile01.com/category.php?id=8"

    # p = Page(target)
    #
    # print(p.source)
    # for a in p.get_links(attrs={"class": "title ", "href": re.compile(r"\.html$")}): print(a)
    # for a in p.get_links(): print(a)

    # xpath = "//*[@id=\"yui_3_9_1_1_1450192409807_1712\"]"
    #
    # print(BeautifulSoup(p.source, "html.parser").find_all(None, attrs={"class": "title "}))

    # print(quote("http://www.google.com/?id=中文"))

    # with open("d:\\zzz\\1.htm", "wb+") as f:
    #     f.write("test".encode())

    # print(url2pathname("http://www.cpouyang.com/index.asp?id=123#haha"))
    # print(url2pathname("https://www.cpouyang.com/index.asp?id=123#haha"))
    # print(url2pathname("mailto://www.cpouyang.com/index.asp?id=123#haha"))
    # print(url2pathname("ftp://www.cpouyang.com/index.asp?id=123#haha"))
    #
    # print(os.path.dirname(url2pathname("http://www.cpouyang.com/index.asp?id=123#haha")))
    # print(os.path.basename(url2pathname("http://www.cpouyang.com/index.asp?id=123#haha")))

    help({})
