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
        write_post("Python", "I LOVE UNIT-TESTING IN PYTHON!!!!")
        self.assertEquals(len(Post.query.all()), 1)
    
    def test_read_posts(self):
        pass

    def test_read_post(self):
        pass

if __name__ == '__main__':
    unittest.main()
