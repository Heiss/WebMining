from os import getcwd
from sqlalchemy import Table, MetaData
from urllib.parse import urlparse
from urllib import request
import ssl
import xml.etree.ElementTree as ET


class Feed:
    def __init__(self, conn):
        self.engine = conn
        self.sites = []

    # Load all feeds from given database
    def load_new_articles(self):
        meta = MetaData()
        website_table = Table('website', meta, autoload=True, autoload_with=self.engine)
        link_table = Table('link', meta, autoload=True, autoload_with=self.engine)
        conn = self.engine.connect()

        links = []

        # read all feed-urls to analyze them
        result = conn.execute(website_table.select())
        idx = 0
        for feed in result:
            content = self.load_url(feed.Feed)
            links = links + self.analyze_xml(content)
            result2 = conn.execute(link_table.select())

            for row in result2:
                try:
                    idx2 = links.index(row.URL)
                except ValueError:
                    idx2 = -1

                if idx2 >= 0:
                    del links[idx2]

            idx += 1

        for link in links:
            domain = urlparse(link).hostname.split('.')[1]
            result = conn.execute(website_table.select().where(website_table.c.Name == domain)).first()
            conn.execute(link_table.insert().values(Website_ID=result.Website_ID, URL=link, Last_Data=""))

        conn.close()

    # read the given file for new feed-urls
    def load_new_feeds_from_file(self, file):
        self.load_file(file)

        meta = MetaData()
        website_table = Table('website', meta, autoload=True, autoload_with=self.engine)
        conn = self.engine.connect()

        # find all sites which are duplicated in the file
        result = conn.execute(website_table.select())
        for row in result:
            try:
                idx = self.sites.index(row.Feed)
            except ValueError:
                idx = -1

            if idx >= 0:
                del self.sites[idx]

        # Insert new sites into the database
        for site in self.sites:
            domain = urlparse(site).hostname.split('.')[1]
            ins = website_table.insert().values(Name=domain, Feed=site)
            conn.execute(ins)

        conn.close()

    # load file for all sites
    def load_file(self, file):
        filename = getcwd() + "/" + file
        self.sites = [line.rstrip('\n') for line in open(filename)]

    def load_url(self, url):
        # For https compatibility
        ssl._create_default_https_context = ssl._create_unverified_context

        req = request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        wp = request.urlopen(req)
        pw = wp.read()

        return pw

    def analyze_xml(self, xmlcontent):
        root = ET.fromstring(xmlcontent)

        links = []
        for child in root[0]:
            if child.tag != "item":
                continue

            for it in child:
                if it.tag == "link":
                    links.append(it.text)
                    break

        return links
