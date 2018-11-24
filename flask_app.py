from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello galera'

if __name__ == '__main__':
    app.run()
    #    app.run(host='localhost', port=8000, debug=True)
