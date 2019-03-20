import redis
import os
redisConnect = redis.Redis(host=os.environ.get('REDIS_HOST') or 'crawler-redis', port=6379, db=0)

def testConnectionRedis():
    try:
        response = redisConnect.client_list()
        if response:
            return 'Connection successful (Redis)'

    except redis.ConnectionError as e:
        print("Error connecting to redis: {}". format(e))