import redis
import os
redisConnect = redis.StrictRedis(host=os.environ.get('REDIS_HOST') or 'crawler-redis', port=6379, db=0)
localRedisConnect = redis.StrictRedis(host='localhost', port=6379, db=0)

POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)

def getVariable(variable_name):
    my_server = redis.Redis(connection_pool=POOL)
    # response = my_server.lrange(variable_name, 0, -1)
    response = my_server.hgetall(variable_name)
    return response

def setVariable(parentURL, parentCrawl):
    my_server = redis.Redis(connection_pool=POOL)
    # my_server.rpush(parentURL, *childurlList)
    my_server.hmset(parentURL, parentCrawl)

def testConnectionRedis():
    try:
        response = redisConnect.ping()
        if response:
            return 'Connection successful (Redis)'

    except redis.ConnectionError as e:
        print("Error connecting to redis: {}". format(e))

def testLocalRedis():
    try:
        response = localRedisConnect.ping()
        if response:
            return 'Connection successful (Redis Local)'

    except redis.ConnectionError as e:
        print("Error connecting to redis(Local): {}". format(e))