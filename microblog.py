from flask import (Flask,
                   render_template,
                   request, redirect,
                   url_for, abort)
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.exc import ProgrammingError
from datetime import datetime
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///microblog"
app.config['USERNAME'] = "username"
app.config['PASSWORD'] = "password"
app.config['MAIL_PORT'] = 5000

# mail = Mail()
# mail.init_app(app)


###DON'T FORGET TO CHANGE THIS!!!
app.config['SECRET_KEY'] = 'blank'

app.debug = True

db = SQLAlchemy(app)

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)


def write_post(title, text, categories=None):
    """Writes post record if title and text exists, or returns Error"""
    if title and text:
        post = Post(title, text)
        db.session.add(post)
        db.session.commit()
    else:
        raise ValueError("Error: title and text required")


def read_posts():
    """Returns all exisitng post records on table"""
    return Post.query.order_by(Post.pub_date.desc()).all()


def read_post(id):
    """Search for post id and return KeyError is not found"""
    if Post.query.get(id):
        return Post.query.get(id)
    else:
        raise KeyError("Error: Post not found")


@app.route('/', methods=['GET'])
def list_view():
    """Sends a response of all exisiting posts"""
    try:
        post_list = read_posts()
        return render_template('lists.html', posts=post_list)
    except ProgrammingError:
        return render_template('lists.html')


@app.route('/post/<int:id>/', methods=['GET'])
def details_view(id):
    """Retrieves existing data """
    try:
        return render_template('details.html', post=read_post(id))
    except KeyError:
        abort(404)


@app.route('/add', methods=['GET', 'POST'])
def add_view():
    """Sends a form if method is GET and writes post if method is POST"""
    if request.method == "POST":
        try:
            write_post(request.form['title'],
                       # request.form['body'])
                       request.form['body'],
                       request.form['categories'])
            return redirect(url_for('list_view'))
        except Exception as e:
            print e
            return redirect(url_for('list_view'))
    else:
        return render_template('add.html')


class Post(db.Model):
    """Post model with title, body, publication date, and user id"""
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
