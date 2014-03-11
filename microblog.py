from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = ""
db = SQLAlchemy(app)


def write_post(title, text):
    post = Post(title, text)
    db.session.add(post)
    db.session.commit()


def read_posts():
    pass
    #return db.query_all()


def read_post(id):
    pass
    # post = Post.query.filter_by(id=id)
    # if post:
    #     return post
    # else:
    #     raise EnvironmentError


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    body = db.Column(db.Text)
    pub_date = db.Column(db.DateTime)

    def __init__(self, title, body):
        self.title = title
        self.body = body
        self.pub_date = datetime.utcnow()

    def __repr__(self):
        return '<Post %r>' % self.title


if __name__ == '__main__':
    app.run(debug=True)
