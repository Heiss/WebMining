from sqlalchemy import create_engine
from time import time, gmtime, strftime, sleep
from Feed import Feed
from Article import Article
from urllib.error import HTTPError


class WebMiner:
    def __init__(self, db):
        self.engine = create_engine("sqlite:///" + db, echo=False)
        self.is_running = True

        self.wait_time = 60
        self.wait_time_on_error = 5

        self.start()

    def loop(self):
        self.loading_feeds()
        self.loading_articles()

    def start(self):
        print("Start program at %s" % (strftime("%Y-%m-%d %H:%M:%S", gmtime())))
        while self.is_running is True:
            print("Run starts at %s" % (strftime("%Y-%m-%d %H:%M:%S", gmtime())))

            # standard time to wait
            time_wait = self.wait_time * 60
            time_start = int(time())

            try:
                self.loop()
            except HTTPError as e:
                print("\nError in urllib.urlopen. [internal server error?]" % (e.read()))
                # reduce time to wait
                time_wait = self.wait_time_on_error * 60

            time_diff = int(time()) - time_start
            time_wait = int(time_wait - time_diff)

            if time_wait > 0:
                print("Wait %smin since %s" % (int(time_wait / 60), strftime("%Y-%m-%d %H:%M:%S", gmtime())))
                sleep(time_wait)
                print("")

    def loading_feeds(self):
        feed = Feed(self.engine)

        print("Check for new feeds: ", end="", flush=True)
        feed.load_new_feeds_from_file("sites")
        print("Done")

        print("Loading feeds: ")
        feed.load_new_articles()

    def loading_articles(self):
        print("Loading articles: ")
        Article(self.engine).load_all_articles()