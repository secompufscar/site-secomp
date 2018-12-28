from flask import Flask, render_template, url_for
from forms import RegistrationForm, LoginForm

app = Flask(__name__)
app.config['SECRET KEY'] = 'a4eaf400f6c89ff7b18f39a3aec47b5c'

"""
This is a simple application to show
the capabilities of flask micro-web-framework
"""

@app.route('/')
def index():
    """
    To render the bootstrap template is necessary
    to add a call to the render_template function
    """
    return render_template('index.html', title='Home Page')

@app.route('/register')
def register():
    form = RegistrationForm()
    return render_template('register.html')

@app.route('/login')
def login():
    form = LoginForm()
    return render_template('login.html')

if __name__ == '__main__':
    app.run()
    #app.run(host='localhost', port=8000, debug=True)
