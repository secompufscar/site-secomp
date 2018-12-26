from flask import Flask, render_template
from flask_bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)

"""
This is a simple application to show
the capabilities of flask micro-web-framework
"""

@app.route('/')
def hello_world():
    """
    To render the bootstrap template is necessary
    to add a call to the render_template function
    """
    return render_template('index.html') 

if __name__ == '__main__':
    app.run()
    #    app.run(host='localhost', port=8000, debug=True)
