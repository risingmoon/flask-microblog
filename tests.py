import unittest
from microblog import db, app, session
from microblog import (
    write_post, read_posts, read_post,
    register, generate_key)
from microblog import Post, Author, Registration
from sqlalchemy.exc import DataError
TITLE = ['Python', 'Javascript', 'Rails', 'iOS']

BODY_TEXT = ["PythonBodyText", "JavascriptBodyTest",
             "RailsBodyText", "iOSBodyText"]


class BasicTest(unittest.TestCase):

    def setUp(self):
        self.db = db
        self.db.create_all()
        self.app = app.test_client()
        self.config = app.config.update(TESTING=True)
        self.email = 'admin@example.com'
        self.username = 'author'
        self.password = 'password'
        author = Author(self.email, self.username, self.password)

        r1 = Registration(
            'person1@example.com',
            'username1',
            'password1')
        generate_key(r1)
        self.db.session.add(r1)

        r2 = Registration(
            'person2@example.com',
            'username2',
            'password2')

        generate_key(r2)
        self.db.session.add(r2)

        self.db.session.add(author)
        self.db.session.commit()

        self.registrant = {
            'email': 'justindavidlee@gmail.com',
            'username': 'risingmoon',
            'password': 'nothing'}

    def tearDown(self):
        self.db.session.remove()
        self.db.drop_all()


class TestView(BasicTest):

    def setup_posts(self):
        author = Author.query.first()
        for num in range(4):
            write_post(TITLE[num], BODY_TEXT[num], author)

    #Works when TESTING=True
    # def test_registration_correct(self):
    #     with self.app as client:
    #         client.get('/register')
    #         client.post('/register', data=dict(
    #             email=self.registrant['email'],
    #             username=self.registrant['username'],
    #             password=self.registrant['password'],
    #             _csrf_token=session.get('_csrf_token'),
    #             follow_redirects=True))
    #     registered = Registration.query.filter_by(
    #         email=self.registrant['email']).first()
    #     self.assertEqual(registered.email, self.registrant['email'])

    def test_confirmation(self):
        author = Author.query.filter_by(username="username1").first()
        self.assertFalse(author)
        registered = Registration.query.filter_by(username="username1").first()
        self.assertTrue(registered)
        with self.app as client:
            client.get('/confirm/' + registered.key)
        author = Author.query.filter_by(username="username1").first()
        self.assertTrue(author)

    def test_registration_post_registered_email(self):
        with self.app as client:
            client.get('/register')
            client.post('/register', data=dict(
                email='person1@example.com',
                username=self.registrant['username'],
                password=self.registrant['password'],
                _csrf_token=session.get('_csrf_token'),
                follow_redirects=True))
        registered = Registration.query.filter_by(
            username=self.registrant['username']).first()
        self.assertIsNone(registered)

    def test_registration_post_registered_username(self):
        with self.app as client:
            client.get('/register')
            client.post('/register', data=dict(
                email=self.registrant['email'],
                username='username1',
                password=self.registrant['password'],
                _csrf_token=session.get('_csrf_token'),
                follow_redirects=True))
        registered = Registration.query.filter_by(
            email=self.registrant['email']).first()
        self.assertIsNone(registered)

    def test_registration_post_author_email(self):
        with self.app as client:
            client.get('/register')
            client.post('/register', data=dict(
                email='admin@example.com',
                username=self.registrant['username'],
                password=self.registrant['password'],
                _csrf_token=session.get('_csrf_token'),
                follow_redirects=True))
        registered = Registration.query.filter_by(
            username=self.registrant['username']).first()
        self.assertIsNone(registered)

    def test_registration_post_author_username(self):
        with self.app as client:
            client.get('/register')
            client.post('/register', data=dict(
                email=self.registrant['email'],
                username='author',
                password=self.registrant['password'],
                _csrf_token=session.get('_csrf_token'),
                follow_redirects=True))
        registered = Registration.query.filter_by(
            email=self.registrant['email']).first()
        self.assertIsNone(registered)

    def test_post_view_empty(self):
        with self.app as client:
            response = client.get("/")
        msg = "No entries here so far"
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
        form_text = """<dt>Username:
      <dd><input type=text name=username>
      <dt>Password:
      <dd><input type=text name=password>
      <dd><input type=submit value=Login>"""
        self.assertIn(form_text, response.data)

    def test_add_view_post_logged_in(self):
        self.setup_posts()
        title = "Perl"
        body = "Perl Body Text"
        with self.app as client:
            client.get('/login')
            # pdb.set_trace()
            client.post('/login', data=dict(
                username=self.username,
                password=self.password,
                _csrf_token=session.get('_csrf_token')),
                follow_redirects=True)
            client.post("/add", data=dict(
                title=title,
                body=body,
                _csrf_token=session.get('_csrf_token')),
                follow_redirects=True)
            current_user = session.get('current_user')
        #Check user logged in
        self.assertTrue(current_user)
        #Check Latest Post
        latest = Post.query.order_by(Post.pub_date.desc()).first()
        self.assertEqual(latest.title, title)
        self.assertEqual(latest.body, body)

    def test_add_view_post_not_logged_in(self):
        self.setup_posts()
        with self.app as client:
            client.get('/login')
            client.post("/add", data=dict(
                title="Perl",
                body="Perl Body Text",
                _csrf_token=session.get('_csrf_token')),
                follow_redirects=True)
            current_user = session.get('current_user')
        self.assertFalse(current_user)
        posts = Post.query.filter_by(title="Perl").all()
        #Post does not contain posting
        self.assertFalse(posts)

    def test_login_get(self):
        with self.app as client:
            response = client.get('/login')
        form_text = """<dt>Username:
      <dd><input type=text name=username>
      <dt>Password:
      <dd><input type=text name=password>
      <dd><input type=submit value=Login>"""
        self.assertIn(form_text, response.data)

    def test_login_correct(self):
        with self.app as client:
            client.get('/login')
            client.post('/login', data=dict(
                username=self.username,
                password=self.password,
                _csrf_token=session.get('_csrf_token')),
                follow_redirects=True)
            self.assertTrue(session.get('current_user'))

    def test_login_incorrect_username(self):
        with self.app as client:
            client.get('/login')
            client.post('/login', data=dict(
                username='wrong',
                password=self.password,
                _csrf_token=session.get('_csrf_token')))
            current_user = session.get('current_user')
        self.assertFalse(current_user)

    def test_login_incorrect_password(self):
        with self.app as client:
            client.get('/login')
            client.post('/login', data=dict(
                username=self.username,
                password='wrong',
                _csrf_token=session.get('_csrf_token')))
            self.assertFalse(session.get('current_user'))

    def test_login_empty(self):
        with self.app as client:
            client.get('/login')
            client.post('/login', data=dict(
                _csrf_token=session.get('_csrf_token')))
            self.assertFalse(session.get('current_user'))

    #When TESTING=True, this stops working
    def test_login_post_forbidden(self):
        """Prevents non-CSRF access"""
        with self.app as client:
            client.get('/login')
            client.post('/login', data=dict(
                username=self.username,
                password=self.password),
                follow_redirects=True)
            self.assertIsNone(session.get('current_user'))

    def test_login_registration_not_confirmed(self):
        """Temp users cannot login"""
        registered = Registration.query.filter_by(username="username1").first()
        self.assertTrue(registered)
        with self.app as client:
            client.get('/login')
            client.post('/login', data=dict(
                username='wrong',
                password=self.password,
                _csrf_token=session.get('_csrf_token')))
            self.assertFalse(session.get('current_user'))

    def test_add_view_post_not_confirmed(self):
        registered = Registration.query.filter_by(username="username1").first()
        self.assertTrue(registered)
        self.setup_posts()
        with self.app as client:
            client.post("/add", data=dict(
                title="Perl",
                body="Perl Body Text",
                _csrf_token=session.get('_csrf_token')),
                follow_redirects=True)
            self.assertFalse(session.get('current_user'))
        posts = Post.query.filter_by(title="Perl").all()
        #Post does not contain posting
        self.assertFalse(posts)

    def test_logout(self):
        with self.app as client:
            client.get('/login')
            client.post('/login', data=dict(
                username=self.username,
                password=self.password,
                _csrf_token=session.get('_csrf_token')),
                follow_redirects=True)
            self.assertTrue(session.get('current_user'))
            client.get('/logout', follow_redirects=True)
            self.assertIsNone(session.get('current_user'))


class MethodTest(BasicTest):

    def setup_posts(self):
        author = Author.query.first()
        for num in range(4):
            write_post(TITLE[num], BODY_TEXT[num], author)

    def test_register_new(self):
        register(self.registrant['email'],
                 self.registrant['username'],
                 self.registrant['password'])
        registrant = Registration.query.filter_by(
            email=self.registrant['email']).first()
        self.assertEquals(registrant.email, self.registrant['email'])
        self.assertEquals(registrant.username, self.registrant['username'])
        self.assertEquals(registrant.password, self.registrant['password'])
        self.assertTrue(registrant.key)

    def test_registered_registration_email(self):
        with self.assertRaises(ValueError):
            register('person1@example.com',
                     self.registrant['username'],
                     self.registrant['password'])

    def test_registered_registration_username(self):
        with self.assertRaises(ValueError):
            register(self.registrant['email'],
                     'username1',
                     self.registrant['password'])

    def test_registered_author_email(self):
        with self.assertRaises(ValueError):
            register("admin@example.com",
                     self.registrant['username'],
                     self.registrant['password'])

    def test_registered_author_username(self):
        with self.assertRaises(ValueError):
            register(self.registrant['email'],
                     'username1',
                     self.registrant['password'])

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
