import redis
import os
redisConnect = redis.Redis(host=os.environ.get('REDIS_HOST') or 'crawler-redis', port=6379, db=0)
localRedisConnect = redis.Redis(host='localhost', port=6379, db=0)

POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)

def getVariable(variable_name):
    my_server = redis.Redis(connection_pool=POOL)
    response = my_server.lrange(variable_name, 0, -1)
    return response

def setVariable(parentURL, childurlList):
    my_server = redis.Redis(connection_pool=POOL)
    my_server.rpush(parentURL, *childurlList)
    
def testConnectionRedis():
    try:
        response = redisConnect.client_list()
        if response:
            return 'Connection successful (Redis)'

    except redis.ConnectionError as e:
        print("Error connecting to redis: {}". format(e))

def testLocalRedis():
    try:
        response = localRedisConnect.client_list()
        if response:
            return 'Connection successful (Redis Local)'

    except redis.ConnectionError as e:
        print("Error connecting to redis(Local): {}". format(e))