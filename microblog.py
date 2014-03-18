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
from flaskext.bcrypt import Bcrypt
from flask_mail import Mail, Message
from random import choice
from flask.ext.seasurf import SeaSurf
import string
# import pdb

app = Flask(__name__)
app.config.from_pyfile('config.py')
app.config.update(
    DEBUG=True,
    # EMAIL SETTINGS
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME='',  # FILL OUT
    MAIL_PASSWORD='',  # FILL OUT
    MAIL_DEFAULT_SENDER=("Microblog", '')
)

###DON'T FORGET TO CHANGE THIS!!!
app.debug = True

db = SQLAlchemy(app)

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

csrf = SeaSurf(app)
mail = Mail(app)
bcrypt = Bcrypt(app)


class Author(db.Model):
    """Author model with primary key, username, password"""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(40), unique=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80))
    posts = db.relationship('Post', backref='author',
                            lazy='dynamic')

    def __init__(self, email, username, password):
        self.email = email
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
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))

    def __init__(self, title, body):
        self.title = title
        self.body = body
        self.pub_date = datetime.utcnow()

    def __repr__(self):
        return '<Post %r>' % self.title


class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(32), unique=True)
    email = db.Column(db.String(40), unique=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(20))
    date = db.Column(db.DateTime)

    def __init__(self, email, username, password):
        self.key = ''.join(
            choice(
                string.ascii_letters + string.digits) for i in range(12)
        )
        self.date = datetime.utcnow()
        self.email = email
        self.username = username
        self.password = password

    def __repr__(self):
        return 'REG_KEY: %r' % self.key


def register(email, username, password):
    missing = []
    if not email:
        missing.append(" email")
    if not username:
        missing.append(" username")
    if not password:
        missing.append(" password")
    if email and username and password:
        registrant = Registration(email, username, password)
        db.session.add(registrant)
        db.session.commit()
    else:
        msg = ','.join(missing)
        raise ValueError("The" + msg + "cannot be empty")


def write_post(title, text, author):
    """Writes post record if title and text exists, or returns Error"""
    if title:
        post = Post(title, text)
        post.author = author
        db.session.add(post)
        db.session.commit()
    else:
        raise ValueError("Error: title is required")


def read_posts():
    """Returns all exisitng post records on table"""
    return Post.query.order_by(Post.pub_date.desc()).all()


def read_post(id):
    """Search for post id and return KeyError is not found"""
    post = Post.query.get(id)
    if post:
        return post
    else:
        raise KeyError("Error: Post not found")


def send_mail(username, email):
    msg = Message(
        subject="Registration Confirmation",
        body="""Please click on the link to confirm account:
                  %s""" % (
        url_for("confirm_view",
                key=Registration.query.filter_by(
                    username=username
                ).first().key)),
        recipients=[email])
    mail.send(msg)


@app.route('/register', methods=['POST', 'GET'])
def registration_view():
    error = None

    if request.method == 'POST':
        try:
            register(request.form.get('email'),
                     request.form.get('username'),
                     request.form.get('password'))
            send_mail(request.form.get('username'),
                      request.form.get('email'))
            flash('A confirmation mail has been sent to your email')
            return redirect(url_for('list_view'))
        except ValueError as e:
            error = e
    return render_template('register.html', error=error)


@app.route('/confirm/<key>')
def confirm_view(key):
    registrant = Registration.query.filter_by(key=key).first()
    if registrant:
        author = Author(
            registrant.email,
            registrant.username,
            registrant.password)
        db.session.add(author)
        db.session.commit()
        db.session.delete(registrant)
        flash('Affirmative. Please login.')
        return redirect(url_for('login'))
    else:
        abort(403)


@app.route('/', methods=['GET'])
def list_view():
    """Sends a response of all existing posts"""
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
    if 'current_user'in session:
        if request.method == "POST":
            try:
                author = Author.query.filter_by(
                    username=session['current_user']).first()
                write_post(request.form.get('title'), request.form.get('body'),
                           author)
                return redirect(url_for('list_view'))
            except ValueError:
                flash("Error: title is required")
                return render_template('add.html')
        else:
            return render_template('add.html')
    else:
        error = "You are not logged in"
        return render_template('login.html', error=error)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Receives response and matches username and password"""
    error = None
    if request.method == 'POST':
        if 'username' in request.form:
            author = Author.query.filter_by(
                username=request.form['username']).first()
            if author:
                if request.form['username'] == author.username \
                        and request.form['password'] == author.password:
                    session['current_user'] = request.form['username']
                    flash('You are logged in')
                    return redirect(url_for('list_view'))
                else:
                    error = 'Invalid password'
            else:
                error = 'We do not have this username in our records'
        else:
            error = "Please provide a username and password"
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('current_user', None)
    flash('You are logged out')
    return redirect(url_for('list_view'))


if __name__ == '__main__':
    # db.create_all()
    # app.run()
    manager.run()
