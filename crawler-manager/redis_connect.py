import logging
import redis
import os
import tempfile

REDIS_HOST = os.environ.get('REDIS_HOST','crawler-redis')
redis_db = redis.Redis(host=REDIS_HOST, port=6379, db=0)

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
        logging.error('Attempting to connect to Redis: ')
        logging.error(REDIS_HOST)

        response = redis_db.ping()
        if response:
            return 'Connection successful (Redis Local)'

    except redis.ConnectionError as e:
        logging.warning('Error connecting to redis(Local): %s'. str(e))
