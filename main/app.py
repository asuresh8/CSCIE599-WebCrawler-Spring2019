from app_configure import app
import flask
import requests
from redis_connect import testConnectionRedis
from mysql_connect import createDatabase, getMysqlConnection

session = requests.Session()
session.trust_env = False

@app.route('/')
def main():
    return flask.render_template("index.html")

@app.route('/crawler/manager')
def manager():
    response  = session.get("http://crawler-manager:8002/")
    return response.text

@app.route('/crawler')
def crawler():
    response  = session.get("http://crawler:8003/")
    return response.text

def testConnections():
    print(testConnectionRedis())
    createDatabase('test')
    mysql = getMysqlConnection()
    if mysql:
        print('Connection successful (MySQL)')
        mysql.close()

if __name__ == "__main__":
    testConnections()
    app.run(debug=True, host="0.0.0.0", port=8001)