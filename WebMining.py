from sqlalchemy import create_engine
from time import time, gmtime, strftime, sleep
from Feed import Feed
from Article import Article


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

            f1 = open('./error.log', 'a')
            f1.write("%s : New session started...\n" % (strftime("%Y-%m-%d %H:%M:%S", gmtime())))

            try:
                self.loop()
            except Exception as e:
                f1 = open('./error.log', 'a')
                f1.write("%s : Error appeared: %s \n" % (strftime("%Y-%m-%d %H:%M:%S", gmtime()), e))
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
        Article(self.engine).check_articles_limited()
