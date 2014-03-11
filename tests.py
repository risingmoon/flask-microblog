import unittest
from microblog import write_post, db, Post


class MicroblogTest(unittest.TestCase):

    def setUp(self):
        self.db = db
        self.db.create_all()

    def tearDown(self):
        self.db.drop_all()

    def test_empty_database(self):
        self.assertEquals(len(Post.query.all()), 0)

    def test_write_post(self):
        title = "Python"
        body = "I LOVE UNIT-TESTING IN PYTHON!!!!"
        write_post(title, body)
        self.assertEquals(len(Post.query.all()), 1)
        post = Post.query.all()[0]
        #Test Attributes
        self.assertEquals(post.title, title)
        self.assertEquals(post.body, body)
        self.assertTrue(post.pub_date)

    def test_long_title(self):
        write_post("""THOU HAST WRITTEN A RIDICULOUS TITLE
                    THAT SHALL EXCEED THE MAXIMIUM THRESHOLD ALLOWED""",
                    "I LOVE UNIT-TESTING IN PYTHON!!!!")

    def test_empty_title(self):
        with self.assertRaises(ValueError):
            write_post(None, "I LOVE UNIT-TESTING IN PYTHON!!!!")

    def test_read_posts(self):
        pass

    def test_read_post(self):
        pass

if __name__ == '__main__':
    unittest.main()
