# WebMining

Not for use in production

A xml-crawler, which crawls specified site-feeds (in *sites* file in root) to save all posts on this websites with the content. After one hour, it will visit the posts again and check for changes. This changes will be saved in the database as a diff from previous snapshot.

All sites will be visited by its own thread, so it is faster then single-threaded.

# Dependancies

- sqlalchemy
- sqlalchemy-migrate
- sqlite3
- python3
- a lot more (diffhelper)

# Usage

Write **python WebMining.py help** into console to get the help-message for usage.

# Important Notices

**The script is not well documented.** You have to add your feed-urls into the *sites*-file in root to crawl them. They will be added into the database at next program start.

