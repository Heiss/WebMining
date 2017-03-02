import ssl
from urllib import request
from sqlalchemy import Table, MetaData
from bs4 import BeautifulSoup
from difflib import unified_diff
from json import dumps, loads
from datetime import datetime
from DiffHelper import make_patch


def decode(cur_soup):
    return cur_soup.prettify("ascii").decode()


def load_article(url):
    # download the given article
    # For https compatibility
    ssl._create_default_https_context = ssl._create_unverified_context

    req = request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    wp = request.urlopen(req)
    pw = wp.read()

    return pw


def analyze_content(last_data, content):
    # analyze the 2 given strings
    # FIXME: this could be cause errors
    diff = unified_diff(last_data.splitlines(keepends=True), content.splitlines(keepends=True))

    # list prints an error, if there are no differences
    try:
        diff = list(diff)
    except TypeError:
        diff = []

    return diff


class Article:
    def __init__(self, conn):
        self.engine = conn

    def load_all_articles(self):
        meta = MetaData()

        link_table = Table('link', meta, autoload=True, autoload_with=self.engine)
        data_table = Table('data', meta, autoload=True, autoload_with=self.engine)
        conn = self.engine.connect()

        result = conn.execute(link_table.select())
        for row in result:
            content = load_article(row.URL)

            curSoup = BeautifulSoup(content, 'html.parser')

            # check if that is not the first time that we saved sth for this article
            if row.Last_Data:
                last_data = row.Last_Data

                # get title, body and the difference between last_data and now
                prettify = decode(curSoup)
                diff = make_patch(last_data, prettify)
                diff_size = len(diff.split("\n"))

                # check if there are any difference (Also an empty string is 1)
                if diff_size > 1:
                    # insert the difference into the database and update the last_data in site table
                    # ndiff is dumped via json https://docs.python.org/3.6/library/difflib.html#difflib.ndiff
                    self.insertData(conn, data_table, diff, row)
                    self.updateLastData(conn, prettify, link_table, row)

            else:
                # we dont need to save the meta shit
                # FIXME: is this the way to work with json-encoding problems?
                self.updateLastData(conn, decode(curSoup), link_table, row)

        conn.close()

    def insertData(self, conn, data_table, prettifyString, row):
        conn.execute(
            data_table.insert().values(Site_ID=row.Site_ID, Timestamp=datetime.now(), Data=prettifyString))

    def updateLastData(self, conn, prettifyString, link_table, row):
        conn.execute(
            link_table.update().where(link_table.c.Site_ID == row.Site_ID).values(
                Last_Data=prettifyString))
