import logging
import redis
import os

redis_db = redis.Redis(host=os.environ.get('REDIS_HOST','0.0.0.0'), port=6379, db=0)


def get(key):
    return redis_db.get(key)


def put(key, value):
    return redis_db.set(key, value)


def exists(key):
    return bool(redis_db.exists(key))


def test_redis_connection():
    try:
        logging.info("Connecting to Redis: %s", os.environ.get('REDIS_HOST','0.0.0.0'))
        response = redis_db.ping()
        if response:
            return 'Connection successful (Redis)'

    except redis.ConnectionError as e:
        logging.error("Error connecting to redis: %s", str(e))