from flask import Flask, flash, redirect, render_template, request, url_for
from flask_debugtoolbar import DebugToolbarExtension

debugToolbar = DebugToolbarExtension()
app = Flask(__name__, template_folder='../templates')
app.secret_key = 'some_secret'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'secret':
            error = 'Invalid credentials'
        else:
            flash(message='You were successfully logged in.', category='error')
            return redirect(url_for('index'))
    return render_template('login.html', error=error)


if __name__ == "__main__":
    app.debug = True
    debugToolbar.init_app(app)
    app.run()