from flask import (Flask,
                   render_template,
                   request, redirect,
                   url_for,
                   session,
                   abort,
                   flash)
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
#from jinja2 import Template

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///microblog"
app.config['USERNAME'] = "test"
app.config['PASSWORD'] = "one"

###DON'T FORGET TO CHANGE THIS!!!
app.config['SECRET_KEY'] = 'blank'

app.debug = True

db = SQLAlchemy(app)

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)


def write_post(title, text):
    """Writes post record if title and text exists, or returns Error"""
    if title and text:
        post = Post(title, text,)
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
        raise KeyError("Error: Key not found")


@app.route('/', methods=['GET'])
def list_view():
    """Sends a response of all exisiting posts"""
    post_list = read_posts()
    return render_template('lists.html', posts=post_list)


@app.route('/post/<int:id>/', methods=['GET'])
def details_view(id):
    """Retrieves existing data """
    try:
        return render_template('details.html', post=read_post(id))
    except ValueError:
        abort(404)


@app.route('/add', methods=['GET', 'POST'])
def add_view():
    """Sends a form if method is GET and writes post if method is POST"""
    if request.method == "POST":
        try:
            write_post(request.form['title'], request.form['body'])
            return redirect(url_for('list_view'))
        except ValueError:
            return redirect(url_for('list_view'))
    else:
        
        return render_template('add.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Receives response and matches username and password"""
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            session['current_user'] = request.form['username']
            flash('You were logged in')
            return redirect(url_for('list_view'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('list_view'))


class Author(db.Model):
    """Author/User model with primary key, username, password"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(30))
    posts = db.relationship('Post', backref='author',
                            lazy='dynamic')

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<Author %r>' % self.username


class Post(db.Model):
    """Post model with title, body, publication date, and author id"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    body = db.Column(db.Text)
    pub_date = db.Column(db.DateTime)

    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))

    def __init__(self, title, body):
        self.title = title
        self.body = body
        self.pub_date = datetime.utcnow()
        self.author_id = Author.query.\
            filter(Author.username == session['current_user']).\
            first().id

    def __repr__(self):
        return '<Post %r>' % self.title

if __name__ == '__main__':
    manager.run()
