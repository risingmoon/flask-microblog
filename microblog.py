from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///microblog"
db = SQLAlchemy(app)

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)


def write_post(title, text):
    if title and text:
        post = Post(title, text)
        db.session.add(post)
        db.session.commit()
    else:
        raise ValueError("Error: title and text required")


def read_posts():
    return Post.query.order_by(Post.pub_date.desc()).all()


def read_post(id):
    if Post.query.get(id):
        return Post.query.get(id)
    else:
        raise KeyError("Error: Key not found")


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
    manager.run()
