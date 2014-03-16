import unittest
from flask import request
from microblog import (app,
                    write_post,
                    read_posts,
                    db,
                    Post,
                    read_post,
                    session)
from sqlalchemy.exc import DataError
import random
import string


TITLE_LIST = ['Python', 'Javascript', 'Rails', 'iOS']

BODY_TEXT = """
Lorem ipsum dolor sit amet, consectetuer
adipiscing elit, sed diam nonummy nibh
euismod tincidunt ut laoreet dolore magna
aliquam erat volutpat."""




# class NonUserTest(unittest.TestCase):
#     pass


class UserTest(unittest.TestCase):

    def setUp(self):
        self.db = db
        self.db.create_all()
        self.app = app.test_client()
        self.username = 'username'
        self.password = 'password'

    def tearDown(self):
        self.db.session.remove()
        self.db.drop_all()

    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout',
                            follow_redirects=True)

    def populate_post(self):
        self.login(self.username, self.password)
        for title in TITLE_LIST:
            import pdb; pdb.set_trace()
            write_post(title, BODY_TEXT)

    def test_list_view_url(self):
        with self.app as client:
            client.get('/')
            assert request.path == '/'

    def test_list_view(self):
        self.populate_post()
        with self.app as client:
            rv = client.get('/')
            for title in TITLE_LIST:
                self.assertIn(title, rv.data)

#     def test_details_view(self):
#         with self.app as client:
#             client.get('/posts/1')

#     def test_empty_database(self):
#         self.assertEquals(len(Post.query.all()), 0)

#     def test_write_post(self):
#         title = "Python"
#         body = "I LOVE UNIT-TESTING IN PYTHON!!!!"
#         write_post(title, body)
#         self.assertEquals(len(Post.query.all()), 1)
#         post = Post.query.all()[0]
#         #Test Attributes
#         self.assertEquals(post.title, title)
#         self.assertEquals(post.body, body)
#         self.assertTrue(post.pub_date)

#     def test_long_title(self):
#         with self.assertRaises(DataError):
#             write_post(
#                 """THOU HAST WRITTEN A RIDICULOUS TITLE THAT
#                 SHALL EXCEED THE MAXIMIUM THRESHOLD ALLOWED""",
#                 "I LOVE UNIT-TESTING IN PYTHON!!!!")

#     def test_empty_title(self):
#         with self.assertRaises(ValueError):
#             write_post(None, "I LOVE UNIT-TESTING IN PYTHON!!!!")

#     def test_empty_body(self):
#         with self.assertRaises(ValueError):
#             write_post("Python", None)

#     def test_read_posts(self):
#         title_lists = ['Python', 'Javascript', 'Rails', 'iOS']
#         self.write_posts(title_lists)
#         post_list = read_posts()
#         title_lists.reverse()
#         for index in range(4):
#             self.assertEquals(post_list[index].title, title_lists[index])

#     def test_read_post(self):

#         for index in range(1, 5):
#             self.assertTrue(read_post(index))
#         with self.assertRaises(KeyError):
#             read_post(6)


# class ViewTest(unittest.TestCase):

#     def login(self, username, password):
#         return self.app.post('/login', data=dict(
#             username=username,
#             password=password
#         ), follow_redirects=True)

#     def logout(self):
#         return self.app.get('/logout', follow_redirects=True)

#     def test_list_view(self):
#         pass

#     def test_details_view(self):
#         pass

#     def test_add_view(self):
#         pass

if __name__ == '__main__':
    unittest.main()
