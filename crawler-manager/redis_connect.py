import logging
import redis
import os
import tempfile

redis_db = redis.Redis(host=os.environ.get('REDIS_HOST','0.0.0.0'), port=6379, db=0)

def get(key):
    return redis_db.get(key)


def exists(key):
    return bool(redis_db.exists(key))


def put(key, value):
    return redis_db.set(key, value)


def write_data_to_file():
    fd, path = tempfile.mkstemp()
    with os.fdopen(fd, 'w') as tmp:
        keys = redis_db.keys()
        for key in keys:
            value = redis_db.get(key)
            tmp.write('{},{},\n'.format(key, value))
    
    return path


def test_redis_connection():
    try:
        logging.info('Attempting to connect to Redis: 0.0.0.0:6379')
        response = redis_db.ping()
        if response:
            return 'Connection successful (Redis Local)'

    except redis.ConnectionError as e:
        logging.warning('Error connecting to redis(Local): %s'. str(e))