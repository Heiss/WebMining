from WebMining import WebMiner
from Manage import Manager
from sys import argv

if __name__ == "__main__":
    if len(argv) == 2:
        WebMiner(argv[1])
    if len(argv) == 4 and argv[1] == "db":
        # TODO: implement the Manage.py and use it here
        Manager(argv[3], argv[2])
    if len(argv) == 5 and argv[1] == "feed":
        # TODO: implement the Manage.py and use it here
        Manager(argv[3], argv[2], argv[4])
    else:
        print(
            """Usage: python WebMining.py <path>
<path> : Provide a path to a SQLite3-file. Absolute starts with a leading Slash (/).

Usage: python WebMining.py db <path> <reset|create>
<reset>\t : Resets the database in given db file.
<create>\t : Create a database for the given <path> file.

Usage: python WebMining.py feed <path> <add|remove> <feed-url>
<add>\t : Add the given <feed-url> in the given <path> databases.
<remove>\t : Remove the given <feed-url> in the given <path> databases. Do nothing, if it doesnt exists.""")
