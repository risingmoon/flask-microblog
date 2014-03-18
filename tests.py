import unittest
# import pdb
from microblog import db, app, session
from microblog import (write_post, read_posts, read_post, register)
from microblog import Post, Author, Registration
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
        self.email = 'admin@example.com'
        self.username = 'author'
        self.password = 'password'
        author = Author(self.email, self.username, self.password)
        self.db.session.add(author)
        self.db.session.commit()

        self.registrant = {
            'email': 'justindavidlee@gmail.com',
            'username': 'risingmoon',
            'password': 'nothing'}

    def tearDown(self):
        self.db.session.remove()
        self.db.drop_all()

    def setup_posts(self):
        author = Author.query.first()
        for num in range(4):
            write_post(TITLE[num], BODY_TEXT[num], author)

    def test_registration_get(self):
        with self.app as client:
            response = client.get('/register')
        form_text = """<dt>Email:
      <dd><input type=text name=email>
      <dt>Username:
      <dd><input type=text name=username>
      <dt>Password:
      <dd><input type=password name=password>
      <dd><input type=submit value=Register>"""
        self.assertIn(form_text, response.data)

    def test_registration_correct(self):
        with app.test_request_context():
            client.get('/register')
            response = client.post('/register', data=dict(
                email=self.registrant.get('email'),
                username=self.registrant.get('username'),
                password=self.registrant.get('password'),
                _csrf_token=session.get('_csrf_token'),
                follow_redirects=True)
            with mail.record_messages() as outbox:

        
    def test_registration_post_empty_email(self):
        pass

    def test_registration_post_empty_username(self):
        pass

    def test_registration_post_empty_password(self):
        pass

    # def test_list_view_empty(self):
    #     with self.app as client:
    #         response = client.get("/")
    #     msg = "Inconcievable.  No entries here so far"
    #     self.assertIn(msg, response.data)

    # def test_list_view_filled(self):
    #     self.setup_posts()
    #     post_list = Post.query.all()
    #     with self.app as client:
    #         response = client.get("/")
    #     for num in range(4):
    #         self.assertIn(post_list[num].title, response.data)

    # def test_details_view(self):
    #     self.setup_posts()
    #     post_list = Post.query.all()
    #     for num in range(4):
    #         url = "/post/" + str(num + 1)
    #         with self.app as client:
    #             response = client.get(url)
    #         self.assertIn(post_list[num].title, response.data)
    #         self.assertIn(post_list[num].body, response.data)
    #         # self.assertIn(post_list[num].pub_date, response.data)
    #         self.assertIn(self.username, response.data)

    # def test_details_view_not_found(self):
    #     self.setup_posts()
    #     with self.app as client:
    #         response = client.get("/post/5")
    #         self.assertIn("Not Found", response.data)

    # def test_add_view_get(self):
    #     with self.app as client:
    #         response = client.get("/add")
    #     form_text = """<dt>Username:
    #   <dd><input type=text name=username>
    #   <dt>Password:
    #   <dd><input type=text name=password>
    #   <dd><input type=submit value=Login>"""
    #     self.assertIn(form_text, response.data)

    # def test_add_view_post_logged_in(self):
    #     self.setup_posts()
    #     with self.app as client:
    #         client.get('/login')
    #         client.post('/login', data=dict(
    #             username=self.username,
    #             password=self.password,
    #             _csrf_token=session['_csrf_token']),
    #             follow_redirects=True)
    #         response = client.post("/add", data=dict(
    #             title="Perl",
    #             body="Perl Body Text",
    #             _csrf_token=session['_csrf_token']),
    #             follow_redirects=True)
    #     #Check Latest Post
    #     latest = Post.query.order_by(Post.pub_date.desc()).first()
    #     self.assertIn(latest.title, response.data)
    #     #Check all posts
    #     post_list = Post.query.all()
    #     for num in range(5):
    #         self.assertIn(post_list[num].title, response.data)

    # def test_add_view_post_not_logged_in(self):
    #     self.setup_posts()
    #     with self.app as client:
    #         client.get('/login')
    #         response = client.post("/add", data=dict(
    #             title="Perl",
    #             body="Perl Body Text",
    #             _csrf_token=session['_csrf_token']),
    #             follow_redirects=True)
    #     self.assertIn("You are not logged in", response.data)

    # def test_add_view_post_empty_title(self):
    #     with self.app as client:
    #         client.get('/login')
    #         response = client.post('/login', data=dict(
    #             username=self.username,
    #             password=self.password,
    #             _csrf_token=session['_csrf_token']),
    #             follow_redirects=True)
    #         response = client.post("/add", data=dict(
    #             title=None,
    #             body="Perl Body Text",
    #             _csrf_token=session['_csrf_token']),
    #             follow_redirects=True)
    #     self.assertIn("Error: title is required", response.data)

    # def test_login_get(self):
    #     with self.app as client:
    #         response = client.get('/login')
    #     form_text = """<dt>Username:
    #   <dd><input type=text name=username>
    #   <dt>Password:
    #   <dd><input type=text name=password>
    #   <dd><input type=submit value=Login>"""
    #     self.assertIn(form_text, response.data)

    # def test_login_correct(self):
    #     with self.app as client:
    #         client.get('/login')
    #         response = client.post('/login', data=dict(
    #             username=self.username,
    #             password=self.password,
    #             _csrf_token=session['_csrf_token']),
    #             follow_redirects=True)
    #     self.assertIn("You are logged in", response.data)

    # def test_login_incorrect_username(self):
    #     with self.app as client:
    #         client.get('/login')
    #         response = client.post('/login', data=dict(
    #             username='wrong',
    #             password=self.password,
    #             _csrf_token=session['_csrf_token']))
    #     self.assertIn("We do not have this username in our records",
    #                   response.data)

    # def test_login_incorrect_password(self):
    #     with self.app as client:
    #         client.get('/login')
    #         response = client.post('/login', data=dict(
    #             username=self.username,
    #             password='wrong',
    #             _csrf_token=session['_csrf_token']))
    #     self.assertIn("Invalid password", response.data)

    # def test_login_empty(self):
    #     with self.app as client:
    #         client.get('/login')
    #         response = client.post('/login', data=dict(
    #             _csrf_token=session['_csrf_token']))
    #     self.assertIn("Please provide a username and password", response.data)

    # def test_login_post_no_record(self):
    #     with self.app as client:
    #         client.get('/login')
    #         response = client.post('/login', data=dict(
    #             username=self.registrant['username'],
    #             password=self.registrant['password'],
    #             _csrf_token=session['_csrf_token']),
    #             follow_redirects=True)
    #     self.assertIn("We do not have this username in our records",
    #                   response.data)

    # def test_login_post_forbidden(self):
    #     #Forbidden access directly from post
    #     with self.app as client:
    #         client.get('/login')
    #         response = client.post('/login', data=dict(
    #             username=self.username,
    #             password=self.password),
    #             follow_redirects=True)
    #     self.assertIn("Forbidden", response.data)

    # def test_logout(self):
    #     with self.app as client:
    #         client.post('/login', data=dict(
    #             username=self.username,
    #             password=self.password),
    #             follow_redirects=True)
    #         response = client.get('/logout', follow_redirects=True)
    #     self.assertIn('You are logged out', response.data)


# class MethodTest(unittest.TestCase):

#     def setUp(self):
#         self.db = db
#         self.db.drop_all()
#         self.db.create_all()
#         self.email = 'admin@example.com'
#         self.username = 'author'
#         self.password = 'password'
#         self.registrant = {
#             'email': 'justindavidlee@gmail.com',
#             'username': 'risingmoon',
#             'password': 'nothing'}
#         author = Author(self.email, self.username, self.password)
#         self.db.session.add(author)
#         self.db.session.commit()

#     def tearDown(self):
#         self.db.session.remove()
#         self.db.drop_all()

#     def setup_posts(self):
#         author = Author.query.first()
#         for num in range(4):
#             write_post(TITLE[num], BODY_TEXT[num], author)

#     def test_register_new(self):
#         register(self.registrant['email'],
#                  self.registrant['username'],
#                  self.registrant['password'])
#         registrant = Registration.query.filter_by(
#             email=self.registrant['email']).first()
#         self.assertEquals(registrant.email, self.registrant['email'])
#         self.assertEquals(registrant.username, self.registrant['username'])
#         self.assertEquals(registrant.password, self.registrant['password'])
#         self.assertTrue(registrant.key)

#     def test_register_empty_email(self):
#         with self.assertRaises(ValueError):
#             register(None,
#                      self.registrant['username'],
#                      self.registrant['password'])

#     def test_register_empty_username(self):
#         with self.assertRaises(ValueError):
#             register(self.registrant['email'],
#                      None,
#                      self.registrant['password'])

#     def test_register_empty_password(self):
#         with self.assertRaises(ValueError):
#             register(self.registrant['email'],
#                      self.registrant['username'],
#                      None)

#     def test_empty_database(self):
#         self.assertEquals(len(Post.query.all()), 0)

#     def test_write_post(self):
#         author = Author.query.first()
#         write_post(TITLE[0], BODY_TEXT[0], author)
#         self.assertEquals(len(Post.query.all()), 1)
#         post = Post.query.all()[0]

#         #Test Attributes
#         self.assertEquals(post.title, TITLE[0])
#         self.assertEquals(post.body, BODY_TEXT[0])
#         self.assertTrue(post.pub_date)
#         self.assertEqual(post.author.username, self.username)

#     def test_long_title(self):
#         author = Author.query.first()
#         with self.assertRaises(DataError):
#             write_post(
#                 """THOU HAST WRITTEN A RIDICULOUS TITLE THAT
#                 SHALL EXCEED THE MAXIMIUM THRESHOLD ALLOWED""",
#                 "I LOVE UNIT-TESTING IN PYTHON!!!!", author)

#     def test_empty_title(self):
#         author = Author.query.first()
#         with self.assertRaises(ValueError):
#             write_post(None, "I LOVE UNIT-TESTING IN PYTHON!!!!", author)

#     def test_read_posts(self):
#         self.setup_posts()
#         post_list = read_posts()
#         TITLE.reverse()
#         BODY_TEXT.reverse()
#         for index in range(4):
#             self.assertEquals(post_list[index].title, TITLE[index])
#             self.assertEquals(post_list[index].body, BODY_TEXT[index])
#             self.assertEquals(post_list[index].author.username,
#                               self.username)

#     def test_read_post(self):
#         self.setup_posts()
#         for index in range(1, 5):
#             self.assertTrue(read_post(index))
#         with self.assertRaises(KeyError):
#             read_post(6)

if __name__ == '__main__':
    unittest.main()
