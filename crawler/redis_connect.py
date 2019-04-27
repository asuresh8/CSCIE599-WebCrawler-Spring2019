import json
import logging
import redis
import os

logging.basicConfig(level=logging.INFO)

class Cache:
    def __init__(self):
        self.rediscache = redis.StrictRedis(host=os.environ.get('REDIS_HOST','crawler-redis'), port=6379, db=0)

    def get(self, key):
        return json.loads(self.rediscache.get(key))


    def put(self,key, value):
        return self.rediscache.set(key, json.dumps(value))


    def exists(self, key):
        return bool(self.rediscache.exists(key))


    def dump(self):
        for key in self.rediscache.scan_iter("*"):
            logging.info('redis value %s --- %s', key, self.rediscache.get(key))
    
    def ping(self):
        try:
           logging.info("Connecting to Redis: %s", os.environ.get('REDIS_HOST','crawler-redis'))
           self.rediscache.ping()
           return 'Connection successful (Redis)'
        except redis.ConnectionError as e:
            logging.error("Error connecting to redis: %s", str(e))    



