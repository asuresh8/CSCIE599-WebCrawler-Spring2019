import flask
from redis_connect import testConnectionRedis
from mysql_connect import getMysqlConnection

app = flask.Flask(__name__)

@app.route('/')
def main():
    return 'Crawler'

def testConnections():
    print(testConnectionRedis())
    mysql = getMysqlConnection()
    if mysql:
        print('Connection successful (MySQL)')
        mysql.close()

if __name__ == "__main__":
    testConnections()
    app.run(debug=True, host="0.0.0.0", port=8003)