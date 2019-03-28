import redis
import os
redisConnect = redis.StrictRedis(host=os.environ.get('REDIS_HOST') or 'crawler-redis', port=6379, db=0)

def testConnectionRedis():
    try:
        print("Connect to Redis: ", os.environ.get('REDIS_HOST'))
        response = redisConnect.ping()
        if response:
            return 'Connection successful (Redis)'

    except redis.ConnectionError as e:
        print("Error connecting to redis: {}". format(e))