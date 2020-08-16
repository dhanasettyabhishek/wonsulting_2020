from flask import Flask, url_for, render_template
from markupsafe import escape
app = Flask(__name__)


@app.route("/")
# @app.route('/hello/')
# @app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)


if __name__ == "__main__":
    app.run(debug=True)
