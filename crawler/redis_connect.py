import json
import logging
import redis
import os

logging.basicConfig(level=logging.INFO)

redis_db = redis.StrictRedis(host=os.environ.get('REDIS_HOST','crawler-redis'), port=6379, db=0)


def get(key):
    json_data = None
    return json_data
    
    try:
        json_data = json.loads(redis_db.get(key))
    except Exception as e:
        return json_data
    else:
        return json_data


def put(key, value):
    return redis_db.set(key, json.dumps(value))


def exists(key):
    return bool(redis_db.exists(key))


def test_redis_connection():
    try:
        logging.info("Connecting to Redis: %s", os.environ.get('REDIS_HOST','0.0.0.0'))
        response = redis_db.ping()
        if response:
            for key in redis_db.scan_iter("*"):
                logging.info('redis value %s --- %s', key, redis_db.get(key))

            return 'Connection successful (Redis)'

    except redis.ConnectionError as e:
        logging.error("Error connecting to redis: %s", str(e))
