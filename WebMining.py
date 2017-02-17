from sqlalchemy import create_engine
from time import time, gmtime, strftime, sleep
from Feed import Feed
from Article import Article
from sys import argv
from urllib.error import HTTPError


class WebMiner:
    def __init__(self, db):
        self.engine = create_engine("sqlite:///" + db, echo=False)
        self.is_running = True
        self.start()

    def loop(self):
        self.loading_feeds()
        self.loading_articles()

    def start(self):
        print("Start program at %s" % (strftime("%Y-%m-%d %H:%M:%S", gmtime())))
        while self.is_running is True:
            print("Run starts at %s" % (strftime("%Y-%m-%d %H:%M:%S", gmtime())))

            # standard time to wait
            time_wait = 20 * 60
            time_start = int(time())

            try:
                self.loop()
            except HTTPError as e:
                print("\nError in urllib.urlopen. [internal server error?]" % (e.read()))
                # reduce time to wait
                time_wait = 5 * 60

            time_diff = int(time()) - time_start
            time_wait = int(time_wait - time_diff)

            if time_wait > 0:
                print("Wait %smin since %s" % (int(time_wait / 60), strftime("%Y-%m-%d %H:%M:%S", gmtime())))
                print("")
            sleep(time_wait)

    def loading_feeds(self):
        feed = Feed(self.engine)

        print("Check for new feeds: ", end='', flush=True)
        feed.load_new_feeds_from_file("sites")
        print("Done")

        print("Loading feeds: ", end='', flush=True)
        feed.load_new_articles()
        print("Done")

    def loading_articles(self):
        print("Loading articles: ", end='', flush=True)
        Article(self.engine).load_all_articles()
        print("Done")


if __name__ == "__main__":
    if len(argv) > 1:
        WebMiner(argv[1])
    else:
        print(
            """Usage: python WebMining.py <PATH>
            <PATH> : Provide a path to a SQLite3-file. Absolute starts with a leading Slash (/).""")
