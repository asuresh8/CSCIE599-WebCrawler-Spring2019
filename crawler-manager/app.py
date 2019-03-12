import flask
from redis_connect import testConnectionRedis, testLocalRedis
from mysql_connect import getMysqlConnection

app = flask.Flask(__name__)

@app.route('/')
def main():
    return 'Crawler-manager'

def testConnections():
    print(testConnectionRedis())
    print(testLocalRedis())
    mysql = getMysqlConnection()
    if mysql:
        print('Connection successful (MySQL)')
        mysql.close()

if __name__ == "__main__":
    testConnections()
    app.run(debug=True, host="0.0.0.0", port=8002)