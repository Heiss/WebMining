import ssl
from urllib import request
from sqlalchemy import Table, MetaData, func, select, and_
from bs4 import BeautifulSoup
from difflib import unified_diff
from datetime import datetime, timedelta
from DiffHelper import make_patch
from urllib.error import HTTPError
from tqdm import tqdm
from sqlalchemy.orm import sessionmaker
from time import gmtime, strftime
from threading import Thread


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


class ArticlesThread(Thread):
    def __init__(self, conn, session, website_id, limit, domain):
        Thread.__init__(self)
        self.engine = conn
        self.session = session
        self.website_id = website_id
        self.limit = limit
        self.domain = domain

    def run(self):
        self.load_all_articles()

    def load_all_articles(self):
        meta = MetaData()

        link_table = Table('link', meta, autoload=True, autoload_with=self.engine)
        data_table = Table('data', meta, autoload=True, autoload_with=self.engine)
        # conn = self.engine.connect()

        # count = session.query(func.count('*')).select_from(link_table).scalar()

        sql = select([link_table.c.Website_ID, link_table.c.Site_ID, link_table.c.URL, link_table.c.Last_Data,
                      link_table.c.Created]).where(and_(link_table.c.Website_ID == self.website_id, link_table)). \
            order_by(link_table.c.Site_ID.desc()).limit(
            self.limit)
        result = self.session.execute(sql)

        # progressbar = result.fetchall()
        progressbar = tqdm(result.fetchall(), position=(self.website_id - 1))
        for row in progressbar:
            progressbar.set_description(desc="%s ID: %s" % (self.domain, row.Site_ID))

            try:
                content = load_article(row.URL)
            except HTTPError as e:
                # if there is an error, we continue with the next URL
                f1 = open('./error.log', 'w+')
                f1.write("%s : Error in urllib.urlopen: [ID: %s, URL: %s]:  %s" % (
                    strftime("%Y-%m-%d %H:%M:%S", gmtime()), row.Site_ID, row.URL, e.read()))
                continue

            curSoup = self.removeGarbage(BeautifulSoup(content, 'html.parser'))

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
                    self.insertData(data_table, diff, row)
                    self.updateLastData(prettify, link_table, row)

            else:
                # we dont need to save the meta shit
                # FIXME: is this the way to work with json-encoding problems?
                self.updateLastData(decode(curSoup), link_table, row)

    def analyze_content(self, last_data, content):
        # analyze the 2 given strings
        # FIXME: this could be cause errors
        differences = unified_diff(last_data.splitlines(keepends=True), content.splitlines(keepends=True))

        # list prints an error, if there are no differences
        try:
            differences = list(differences)
        except TypeError:
            differences = []

        return differences

    def removeGarbage(self, curSoup):
        [x.decompose() for x in curSoup.findAll('script')]
        [x.decompose() for x in curSoup.findAll('style')]
        return curSoup

    def insertData(self, data_table, prettifyString, row):
        self.session.execute(
            data_table.insert().values(Site_ID=row.Site_ID, Timestamp=datetime.now(), Data=prettifyString))

    def updateLastData(self, prettifyString, link_table, row):
        if not row.Created or row.Created is None:
            self.session.execute(
                link_table.update().where(link_table.c.Site_ID == row.Site_ID).values(Created=datetime.now(),
                                                                                      Last_Data=prettifyString))
        else:
            self.session.execute(link_table.update().where(link_table.c.Site_ID == row.Site_ID).values(
                Last_Data=prettifyString))
