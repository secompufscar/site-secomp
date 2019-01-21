from flask import Flask, render_template, url_for
from flask_login import LoginManager

app = Flask(__name__)

if __name__ == '__main__':
    #app.run()
    login_manager = LoginManager()
    app.run(host='localhost', port=8000, debug=True)
    login_manager.init_app(app)

