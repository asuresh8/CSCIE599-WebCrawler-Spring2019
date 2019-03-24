import flask
from redis_connect import testConnectionRedis

app = flask.Flask(__name__)

@app.route('/')
def main():
    return 'Crawler'

def testConnections():
    print(testConnectionRedis())


if __name__ == "__main__":
    testConnections()
    app.run(debug=True, host="0.0.0.0", port=8003)