from flask import Flask
app = Flask(__name__)


def write_post(title, text):
    pass


def read_posts():
    pass


def read_post(id):
    pass

if __name__ == '__main__':
    app.run(debug=True)