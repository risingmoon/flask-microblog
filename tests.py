import unittest
# from flask import request
from microblog import (write_post, app,
                       read_posts, db, read_post)
from microblog import Post, Author
from sqlalchemy.exc import DataError
TITLE = ['Python', 'Javascript', 'Rails', 'iOS']

BODY_TEXT = ["PythonBodyText", "JavascriptBodyTest",
             "RailsBodyText", "iOSBodyText"]


class TestView(unittest.TestCase):

    def setUp(self):
        self.db = db
        self.db.drop_all()
        self.db.create_all()
        self.app = app.test_client()
        self.username = 'author'
        self.password = 'password'
        author = Author(self.username, self.password)
        self.db.session.add(author)
        self.db.session.commit()

    def tearDown(self):
        self.db.session.remove()
        self.db.drop_all()

    def setup_posts(self):
        author = Author.query.first()
        for num in range(4):
            write_post(TITLE[num], BODY_TEXT[num], author)

    def test_list_view_empty(self):
        with self.app as client:
            response = client.get("/")
        msg = "Inconcievable.  No entries here so far"
        self.assertIn(msg, response.data)

    def test_list_view_filled(self):
        self.setup_posts()
        post_list = Post.query.all()
        with self.app as client:
            response = client.get("/")
        for num in range(4):
            self.assertIn(post_list[num].title, response.data)

    def test_details_view(self):
        self.setup_posts()
        post_list = Post.query.all()
        for num in range(4):
            url = "/post/" + str(num + 1)
            with self.app as client:
                response = client.get(url)
            self.assertIn(post_list[num].title, response.data)
            self.assertIn(post_list[num].body, response.data)
            # self.assertIn(post_list[num].pub_date, response.data)
            self.assertIn(self.username, response.data)

    def test_details_view_not_found(self):
        self.setup_posts()
        with self.app as client:
            response = client.get("/post/5")
            self.assertIn("Not Found", response.data)

    def test_add_view_get(self):
        with self.app as client:
            response = client.get("/add")
        form_text = """
    <dl>
      <dt>Username:
      <dd><input type=text name=username>
      <dt>Password:
      <dd><input type=password name=password>
      <dd><input type=submit value=Login>
    </dl>"""
        self.assertIn(form_text, response.data)

    def test_add_view_post_logged_in(self):
        self.setup_posts()
        with self.app as client:
            client.post('/login', data=dict(
                username=self.username,
                password=self.password),
                follow_redirects=True)
            response = client.post("/add", data=dict(
                title="Perl",
                body="Perl Body Text"
            ), follow_redirects=True)
        #Check Latest Post
        latest = Post.query.order_by(Post.pub_date.desc()).first()
        self.assertIn(latest.title, response.data)
        #Check all posts
        post_list = Post.query.all()
        for num in range(5):
            self.assertIn(post_list[num].title, response.data)

    def test_add_view_post_logged_out(self):
        self.setup_posts()
        with self.app as client:
            response = client.post("/add", data=dict(
                title="Perl",
                body="Perl Body Text"
            ), follow_redirects=True)
        self.assertIn("You are not logged in", response.data)

    def test_login(self):
        with self.app as client:
            response = client.get('/login')
        form_text = """
    <dl>
      <dt>Username:
      <dd><input type=text name=username>
      <dt>Password:
      <dd><input type=password name=password>
      <dd><input type=submit value=Login>
    </dl>"""
        self.assertIn(form_text, response.data)

    def test_login_correct(self):
        with self.app as client:
            response = client.post('/login', data=dict(
                username=self.username,
                password=self.password),
                follow_redirects=True)
        self.assertIn("You are logged in", response.data)

    def test_login_incorrect_username(self):
        with self.app as client:
            response = client.post('/login', data=dict(
                username='wrong',
                password=self.password))
        self.assertIn("Invalid username or password", response.data)

    def test_login_incorrect_password(self):
        with self.app as client:
            response = client.post('/login', data=dict(
                username='author',
                password='wrong'))
        self.assertIn("Invalid username or password", response.data)

    def test_login_empty(self):
        pass

    def test_logout(self):
        with self.app as client:
            client.post('/login', data=dict(
                username=self.username,
                password=self.password),
                follow_redirects=True)
            response = client.get('/logout', follow_redirects=True)
        self.assertIn('You are logged out', response.data)

    # def test_add_view_post_empty_title(self):
    #     with self.app as client:
    #         response = client.post("/add", data=dict(
    #             title=None,
    #             body="Perl Body Text"
    #         ))
    #     self.assertIn("Error: title and text required", response.data)


class MethodTest(unittest.TestCase):

    def setUp(self):
        self.db = db
        self.db.drop_all()
        self.db.create_all()
        self.username = 'author'
        self.password = 'password'
        author = Author(self.username, self.password)
        self.db.session.add(author)
        self.db.session.commit()

    def tearDown(self):
        self.db.session.remove()
        self.db.drop_all()

    def setup_posts(self):
        author = Author.query.first()
        for num in range(4):
            write_post(TITLE[num], BODY_TEXT[num], author)

    def test_empty_database(self):
        self.assertEquals(len(Post.query.all()), 0)

    def test_write_post(self):
        author = Author.query.first()
        write_post(TITLE[0], BODY_TEXT[0], author)
        self.assertEquals(len(Post.query.all()), 1)
        post = Post.query.all()[0]

        #Test Attributes
        self.assertEquals(post.title, TITLE[0])
        self.assertEquals(post.body, BODY_TEXT[0])
        self.assertTrue(post.pub_date)
        self.assertEqual(post.author.username, self.username)

    def test_long_title(self):
        author = Author.query.first()
        with self.assertRaises(DataError):
            write_post(
                """THOU HAST WRITTEN A RIDICULOUS TITLE THAT
                SHALL EXCEED THE MAXIMIUM THRESHOLD ALLOWED""",
                "I LOVE UNIT-TESTING IN PYTHON!!!!", author)

    def test_empty_title(self):
        author = Author.query.first()
        with self.assertRaises(ValueError):
            write_post(None, "I LOVE UNIT-TESTING IN PYTHON!!!!", author)

    def test_empty_body(self):
        author = Author.query.first()
        with self.assertRaises(ValueError):
            write_post("Python", None, author)

    def test_read_posts(self):
        self.setup_posts()
        post_list = read_posts()
        TITLE.reverse()
        BODY_TEXT.reverse()
        for index in range(4):
            self.assertEquals(post_list[index].title, TITLE[index])
            self.assertEquals(post_list[index].body, BODY_TEXT[index])
            self.assertEquals(post_list[index].author.username,
                              self.username)

    def test_read_post(self):
        self.setup_posts()
        for index in range(1, 5):
            self.assertTrue(read_post(index))
        with self.assertRaises(KeyError):
            read_post(6)
if __name__ == '__main__':
    unittest.main()
