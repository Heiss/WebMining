import ssl
from urllib import request
from sqlalchemy import Table, MetaData
from bs4 import BeautifulSoup
from difflib import unified_diff
from json import dumps, loads
from datetime import datetime
from DiffHelper import make_patch, apply_patch


class Article:
    def __init__(self, conn):
        self.engine = conn

    def decode(self, cur_soup):
        return cur_soup.body.prettify("ascii").decode()

    def load_all_articles(self):
        meta = MetaData()

        link_table = Table('link', meta, autoload=True, autoload_with=self.engine)
        data_table = Table('data', meta, autoload=True, autoload_with=self.engine)
        conn = self.engine.connect()

        result = conn.execute(link_table.select())
        for row in result:
            content = self.load_article(row.URL)

            curSoup = BeautifulSoup(content, 'html.parser')

            # check if that is not the first time that we saved sth for this article
            if row.Last_Data:
                last_list = loads(row.Last_Data)

                # get title, body and the difference between last_data and now
                diff = self.analyze_content(last_list[1], self.decode(curSoup))
                diff_size = len(diff)

                # check if there are any difference
                if diff_size > 0:
                    # insert the difference into the database and update the last_data in site table
                    # ndiff is dumped via json https://docs.python.org/3.6/library/difflib.html#difflib.ndiff
                    conn.execute(
                        data_table.insert().values(Site_ID=row.Site_ID, Timestamp=datetime.now(), Data=dumps(diff)))

            if not row.Last_Data:
                # we dont need to save the meta shit
                # FIXME: is this the way to work with json-encoding problems?
                data_list = [curSoup.title.string, self.decode(curSoup)]
                conn.execute(
                    link_table.update().where(link_table.c.Site_ID == row.Site_ID).values(
                        Last_Data=dumps(data_list)))

    # download the given article
    def load_article(self, url):
        # For https compatibility
        ssl._create_default_https_context = ssl._create_unverified_context

        req = request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        wp = request.urlopen(req)
        pw = wp.read()

        return pw

    # analyze the 2 given strings
    def analyze_content(self, last_data, content):
        # FIXME: this could be cause errors
        diff = unified_diff(last_data.splitlines(keepends=True), content.splitlines(keepends=True))

        # list prints an error, if there are no differences
        try:
            diff = list(diff)
        except TypeError:
            diff = []

        return diff


