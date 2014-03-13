import unittest
from flask import request
from microblog import app, write_post, read_posts, db, Post, read_post
from sqlalchemy.exc import DataError

# with app.test_client_context()

class MicroblogTest(unittest.TestCase):

    def setUp(self):
        self.db = db
        self.db.create_all()
        self.client = app.test_client()

    def tearDown(self):
        self.db.session.remove()
        self.db.drop_all()

    def test_list_view_url(self):
        with self.client as client:
            rv = client.get('/')
            assert request.path == '/'

    def test_list_view(self):
        title_lists = ['Python', 'Javascript', 'Rails', 'iOS']
        self.write_posts(title_lists)
        with self.client as client:
            rv = client.get('/')
            for title in title_lists:
                self.assertIn(title, rv.data)

    def test_details_view(self):
        with self.client as client:
            rv = client.get('/posts/1')

    def write_posts(self, title_lists):
        for title in title_lists:
            write_post(title, "BLANK BODY")


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
        with self.assertRaises(DataError):
            write_post("""THOU HAST WRITTEN A RIDICULOUS TITLE
                    THAT SHALL EXCEED THE MAXIMIUM THRESHOLD ALLOWED""",
                    "I LOVE UNIT-TESTING IN PYTHON!!!!")

    def test_empty_title(self):
        with self.assertRaises(ValueError):
            write_post(None, "I LOVE UNIT-TESTING IN PYTHON!!!!")

    def test_empty_body(self):
        with self.assertRaises(ValueError):
            write_post("Python", None)

    def test_read_posts(self):
        title_lists = ['Python', 'Javascript', 'Rails', 'iOS']
        self.write_posts(title_lists)
        post_list = read_posts()
        title_lists.reverse()
        for index in range(4):
            self.assertEquals(post_list[index].title, title_lists[index])

    def test_read_post(self):
        title_lists = ['Python', 'Javascript', 'Rails', 'iOS']
        for title in title_lists:
            write_post(title, "BLANK BODY")
        for index in range(1, 5):
            self.assertTrue(read_post(index))
        with self.assertRaises(KeyError):
            read_post(6)

    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)



if __name__ == '__main__':
    unittest.main()
