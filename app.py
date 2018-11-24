from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return 'olá galera'

if __name__ == '__main__':
    app.run(host='localhost', port=8000, debug=True)
