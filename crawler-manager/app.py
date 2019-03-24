import flask
import requests
import aiohttp
import asyncio
from parsel import Selector
import time
import uuid
import os
from redis_connect import testConnectionRedis, testLocalRedis, getVariable, setVariable
from collections import deque

app = flask.Flask(__name__)
start = time.time()


@app.route('/')
def main():
    return 'Crawler-manager'


#Testing Connections
def testConnections():
    print(testConnectionRedis())
    print(testLocalRedis())


if __name__ == "__main__":
    testConnections()
    app.run(debug=True, host="0.0.0.0", port=8002)