import unittest
from flask import request
from microblog import (write_post, app,
                       read_posts, db, Post, read_post)
from sqlalchemy.exc import DataError

TITLE = ['Python', 'Javascript', 'Rails', 'iOS']

BODY_TEXT = ["PythonBodyText", "JavascriptBodyTest",
             "RailsBodyText", "iOSBodyText"]


class MicroblogTest(unittest.TestCase):

    def setUp(self):
        self.db = db
        self.db.create_all()
        self.app = app.test_client()

    def tearDown(self):
        self.db.session.remove()
        self.db.drop_all()

    def setup_posts(self):
        for num in range(4):
            write_post(TITLE[num], BODY_TEXT[num])

    def test_empty_database(self):
        self.assertEquals(len(Post.query.all()), 0)

    def test_write_post(self):
        write_post(TITLE[0], BODY_TEXT[0])
        self.assertEquals(len(Post.query.all()), 1)
        post = Post.query.all()[0]
        #Test Attributes
        self.assertEquals(post.title, TITLE[0])
        self.assertEquals(post.body, BODY_TEXT[0])
        self.assertTrue(post.pub_date)

    def test_long_title(self):
        with self.assertRaises(DataError):
            write_post(
                """THOU HAST WRITTEN A RIDICULOUS TITLE THAT
                SHALL EXCEED THE MAXIMIUM THRESHOLD ALLOWED""",
                "I LOVE UNIT-TESTING IN PYTHON!!!!")

    def test_empty_title(self):
        with self.assertRaises(ValueError):
            write_post(None, "I LOVE UNIT-TESTING IN PYTHON!!!!")

    def test_empty_body(self):
        with self.assertRaises(ValueError):
            write_post("Python", None)

    def test_read_posts(self):
        self.setup_posts()
        post_list = read_posts()
        TITLE.reverse()
        for index in range(4):
            self.assertEquals(post_list[index].title, TITLE[index])

    def test_read_post(self):
        self.setup_posts()
        for index in range(1, 5):
            self.assertTrue(read_post(index))
        with self.assertRaises(KeyError):
            read_post(6)

if __name__ == '__main__':
    unittest.main()
