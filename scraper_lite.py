from bs4 import BeautifulSoup
from urllib.parse import urlparse, quote
from urllib.request import urlopen, urlretrieve, url2pathname
import os, re, time, socket


class Page:
    """Dunno what to write yet"""
    # to be solved: 1.short url
    def __init__(self, url, method="static", waiting=5):
        """type = {"static", "dynamic"}"""
        assert isinstance(url, str)
        # url prefix
        self._url = url if re.findall(r"^http", url) else "http://" + re.sub(r"^/*", r"", url)
        # url parsing
        self._urlparse = urlparse(self._url)
        # encoding checking priority
        self._trials = ("utf8", "cp950", "ascii", "latin1")
        self._waiting = waiting

        # Bind together in action
        self._source = ""
        self._encoding = ""

        assert method.lower() in ("static", "dynamic", "s", "d")
        self._method = "static" if method.lower() in ("static", "s") else "dynamic"

    def _get_source(self):
        """-> str"""
        # have to call time package internally, otherwise would be too late
        from time import sleep
        sleep(self._waiting)
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
                time.sleep(5)
                browser.get(self._url)
                self._source, self._encoding = browser.page_source, None
                browser.close()
                time.sleep(5)
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
                            if re.search(r"\.(php|js|html?|s?html|css|asp)$", link):
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

    root = "e:\\Sscraper" if socket.gethostname() == "Charles-PC"\
        else "f:\\Scraper" if socket.gethostname() == "irenejuju-PC"\
        else "d:\\Scraper"
    
    projs = {
        "Yahoo News Stock": {
            "home": "tw.news.yahoo.com/stock",
            "method": "dynamic",
            "attrs": {
                "class": "title ",
                "href": re.compile(r"\.html$"),
            },
        },
        "Yahoo News Real-estate": {
            "home": "tw.news.yahoo.com/real-estate",
            "method": "dynamic",
            "attrs": {
                "class": "title ",
                "href": re.compile(r"\.html$"),
            },
        },
        "PTT Creditcard": {
            "home": "www.ptt.cc/bbs/creditcard/index.html",
            "attrs": {
                "href": re.compile(r"M\.\d{10}\."),
            },
        },
        "cnYES Headlines": {
            "home": "news.cnyes.com/headline_sitehead/list.shtml",
            "attrs": {
                "href": re.compile(r"\d+\.shtml\?c=headline_sitehead"),
            },
        },
        "cnYES Rollnews": {
            "home": "news.cnyes.com/rollnews/list.shtml",
            "attrs": {
                "href": re.compile(r"\d+\.shtml\?c=detail"),
            },
        },
        "Mobile01 House": {
            "home": "www.mobile01.com/forumtopic.php?c=26",
            "attrs": {
                "href": re.compile(r"^topicdetail\.php\?f=\d+&t=\d+$")
            },
        },
        "CNA Finance": {
            "home": "www.cna.com.tw/list/afe-1.aspx",
            "attrs": {
                "href": re.compile(r"/afe/.+\.aspx$")
            },
        },
        "CNN Asia": {
            "home": "edition.cnn.com/asia",
            "name": "a",
            "attrs": {
                "href": re.compile(r"^/\d+/\d+/\d+/"),
            },
        },
        "BBC TC Business": {
            "home": "www.bbc.com/zhongwen/trad/business",
            "attrs": {
                "href": re.compile(r"/zhongwen/trad/business/\d+/\d+/"),
            },
        },
        "Reuters SC Finance": {
            "home": "cn.reuters.com",
            "link_pages": ["cn.reuters.com/news/archive/financialServicesNews?date=today"],
            "attrs": {
                "href": re.compile(r"^/article/"),
            },
        },
    }
    
    def safewrite(p, b=b""):
        """Check if the directory exists before writing a file"""
        if not os.path.exists(os.path.dirname(p)):
            os.makedirs(os.path.dirname(p))
        with open(p, "wb+") as f:
            f.write(b)
    
    # Prepare CNA Finance
    if "CNA Finance" in projs.keys():
        # Update the dict
        projs["CNA Finance"]["link_pages"] =\
            [re.sub(r"\d+", repr(i), projs["CNA Finance"]["home"], 1) for i in range(1, 4)]
        projs["CNA Finance"]["attrs"] = {
            "href": re.compile(r"/afe/.+\.aspx$"),
        }
    
    # Prepare cnYES Rollnews
    if "cnYES Rollnews" in projs.keys():
        # Update the dict
        ll = []
        ll.append(projs["cnYES Rollnews"]["home"])
        ll.extend([re.sub(r"list(?=\.shtml$)",
                         "list_%s" % repr(i),
                         projs["cnYES Rollnews"]["home"]) for i in range(2, 11)])
        projs["cnYES Rollnews"]["link_pages"] = ll
        projs["cnYES Rollnews"]["attrs"] = {
            "href": re.compile(r"\d+\.shtml\?c=detail"),
        }
    
    # Prepare PTT Creditcard
    if "PTT Creditcard" in projs.keys():
        peek = Page(projs["PTT Creditcard"]["home"])
        # Create link pages
        tmp = peek.get_links(attrs={"href": re.compile(r"index\d{2,}\.html$")}).pop()
        num = int(re.search(r"\d+(?=\.html$)", tmp).group())
        # Update the dict
        projs["PTT Creditcard"]["link_pages"] =\
            [re.sub(r"(?<=index)\d+(?=\.html$)", repr(num - i), tmp) for i in range(3)]
        projs["PTT Creditcard"]["attrs"] = {
            "href": re.compile(r"M\.\d{10}\."),
        }
    
    # Prepare Mobile01 House
    if "Mobile01 House" in projs.keys():
        # Update the dict
        projs["Mobile01 House"]["link_pages"] =\
            [projs["Mobile01 House"]["home"] + "&p=%s" % repr(i+1) for i in range(3)]
        projs["Mobile01 House"]["attrs"] = {
            "href": re.compile(r"^topicdetail\.php\?f=\d+&t=\d+$"),
        }
    
    # Process all projects
    for proj in projs:
        time_stamp = "_".join([time.strftime("%Y%m%d", time.localtime()),
                               # time.strftime("%H%M%S", time.localtime()),
                               ])
        folder = os.path.join(root, proj, time_stamp)
        if not os.path.exists(folder):
            os.makedirs(folder)
        keys = projs[proj].keys()
    
        if "link_pages" not in keys:
            page = Page(projs[proj]["home"], method=projs[proj]["method"] if "method" in keys else "static")
            links = page.get_links(name=projs[proj]["tags"] if "tags" in keys else None,
                                   attrs=projs[proj]["attrs"] if "attrs" in keys else {},
                                   text=projs[proj]["text"] if "text" in keys else None,
                                   limit=projs[proj]["limit"] if "limit" in keys else None)
        else:
            links = []
            for link_page in projs[proj]["link_pages"]:
                page = Page(link_page, method=projs[proj]["method"] if "method" in keys else "static")
                if page.source:
                    tmp = page.get_links(name=projs[proj]["tags"] if "tags" in keys else None,
                                         attrs=projs[proj]["attrs"] if "attrs" in keys else {},
                                         text=projs[proj]["text"] if "text" in keys else None,
                                         limit=projs[proj]["limit"] if "limit" in keys else None)
                    links.extend(tmp)
    
        # handle the file retrieval
        links = sorted(set(links))
        for sn, link in enumerate(links):   # print(link)
            parse = urlparse(link)
            # if not another website
            if parse.path:
                # Must be CLEAN in "conjunction" points when using os.path.join(a, b)
                # Meanwhile, bar sign (|) result in errors in open function
                # Hence we substitute bad signs with underscore (_)
                fname = os.path.join(folder, url2pathname(parse.path).lstrip("\\"))
                if parse.query:
                    fname += "_" + parse.query
                if parse.fragment:
                    fname += "_" + parse.fragment
                if not re.search(r"\.(html?|s?html|aspx?|css|js|xml|php)$", fname):
                    fname += ".html"
                print(":: Next process", fname, "from", link, "(%s/%s)" % (sn+1, len(links)))
                safewrite(fname, Page(link).source.encode())
