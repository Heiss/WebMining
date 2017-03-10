# https://docs.python.org/3/library/unittest.html
import unittest
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from ArticlesThread import decode, Article
from DiffHelper import make_patch, apply_patch


class Tester(unittest.TestCase):
    def setUp(self):
        # TODO: create an example
        with open('tests/test_true.html', 'r') as f:
            self.example_true = BeautifulSoup(''.join(f.readlines()), "lxml")

        with open('tests/test_false.html', 'r') as f:
            self.example_false = BeautifulSoup(''.join(f.readlines()), "lxml")

        self.engine = create_engine("sqlite://", echo=False)

    def test_Article_NotSame(self):
        art = Article(self.engine)
        res = make_patch(decode(self.example_false), decode(self.example_true))
        # res = [l for l in res if l.startswith('+ ') or l.startswith('- ')]

        self.assertTrue(len(res.split("\n")) - 1 > 0)

    def test_Article_Same(self):
        art = Article(self.engine)
        res = make_patch(decode(self.example_true), decode(self.example_true))
        # res = [l for l in res if l.startswith('+ ') or l.startswith('- ')]

        self.assertTrue(len(res.split("\n")) - 1 == 0)

    def test_Article_Restore(self):
        art = Article(self.engine)

        old = decode(self.example_false)
        cur = decode(self.example_true)

        res = make_patch(old, cur)
        rest = apply_patch(cur, res, True)

        self.assertTrue(decode(self.example_false) == rest)
        self.assertFalse(decode(self.example_true) == rest)


if __name__ == '__main__':
    unittest.main()
