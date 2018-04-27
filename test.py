from flask import Flask, render_template

app = Flask(__name__)
app.config['SECRET_KEY'] = "some_secret"


@app.route('/')
def index():
    return render_template('register_success.html')


if __name__ == '__main__':
    app.run()
