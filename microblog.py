from flask import (Flask,
                   render_template,
                   request, redirect,
                   url_for, abort,
                   flash, session)
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.exc import ProgrammingError
from datetime import datetime
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///microblog"
app.config['USERNAME'] = "author"
app.config['PASSWORD'] = "password"
app.config['MAIL_PORT'] = 5000

###DON'T FORGET TO CHANGE THIS!!!
app.config['SECRET_KEY'] = 'blank'

app.debug = True

db = SQLAlchemy(app)

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Receives response and matches username and password"""
    error = None
    if request.method == 'POST':
        author = Author.query.filter(
            Author.username == request.form['username']).first()
        if author and request.form['password'] == author.password:
            session['logged_in'] = True
            session['current_user'] = request.form['username']
            flash('You are logged in')
            return redirect(url_for('list_view'))
        else:
            error = 'Invalid username or password'
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('current_user', None)
    flash('You are logged out')
    return redirect(url_for('list_view'))


def write_post(title, text, author):
    """Writes post record if title and text exists, or returns Error"""
    if title and text:
        post = Post(title, text)
        post.author = author
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


@app.route('/post/<int:id>', methods=['GET'])
def details_view(id):
    """Retrieves existing data """
    try:
        return render_template('details.html', post=read_post(id))
    except KeyError:
        abort(404)


@app.route('/add', methods=['GET', 'POST'])
def add_view():
    """Sends a form if method is GET and writes post if method is POST"""
    if 'logged_in'in session and session['logged_in']:
        if request.method == "POST":
            try:
                author = Author.query.filter(
                    Author.username == session['current_user']).first()
                write_post(request.form['title'],
                           request.form['body'],
                           author)
                return redirect(url_for('list_view'))
            except ValueError:
                print "HERE"
                flash("Error: title and text required")
        else:
            return render_template('add.html')
    else:
        error = "You are not logged in"
        return render_template('login.html', error=error)


class Author(db.Model):
    """Author model with primary key, username, password"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80))
    posts = db.relationship('Post', backref='author',
                            lazy='dynamic')

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<Author %r>' % self.username


class Post(db.Model):
    """Post model with title, body, publication date, and user id"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    body = db.Column(db.Text)
    pub_date = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('author.id'))

    def __init__(self, title, body):
        self.title = title
        self.body = body
        self.pub_date = datetime.utcnow()

    def __repr__(self):
        return '<Post %r>' % self.title

if __name__ == '__main__':
    # manager.run()
    try:
        # db.drop_all()
        # author = Author('author')
        # db.session.add(author)
        # db.session.commit()
        manager.run()
    finally:
        db.session.remove()
        db.drop_all()
