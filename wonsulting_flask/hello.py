from flask import Flask, url_for
from markupsafe import escape
app = Flask(__name__)

@app.route('/')
def index():
    return 'Index Page'

@app.route('/hello')
def hello_world():
    return "Hello, World!"

@app.route('/user/<username>')
def show_user(username):
    return "User is: %s" % escape(username)

@app.route('/username/<username>')
def profile(username):
    return '{}\'s profile'.format(escape(username))

@app.route('/post/<int:post_id>')
def show_post(post_id):
    return 'Post %d' % post_id

@app.route('/path/<path:subpath>')
def show_subpath(subpath):
    return 'Subpath %s' % escape(subpath)

with app.test_request_context():
    print(url_for('index'))
    print(url_for('show_user', username="Abhishek Dhanasetty"))
    print(url_for('profile', username="Abhishek Dhanasetty"))
    print(url_for('hello_world', next='/'))

