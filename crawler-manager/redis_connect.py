import json
import logging
import redis
import os
import tempfile

logging.basicConfig(level=logging.INFO)

REDIS_HOST = os.environ.get('REDIS_HOST', '0.0.0.0')
redis_db = redis.Redis(host=REDIS_HOST, port=6379, db=0)

def get(key):
    return json.loads(redis_db.get(key))


def exists(key):
    return bool(redis_db.exists(key))


def put(key, value):
    return redis_db.set(key, json.dumps(value))


def write_data_to_file():
    fd, path = tempfile.mkstemp()
    with os.fdopen(fd, 'w') as tmp:
        keys = redis_db.keys()
        for key in keys:
            value = redis_db.get(key)
            record = '{},{},\n'.format(key.decode("utf-8"), value.decode("utf-8"))
            logging.info("Writing %s to file", record)
            tmp.write(record)

    return path


def test_redis_connection():
    try:
        logging.info('Attempting to connect to Redis: ')
        logging.info(REDIS_HOST)

        response = redis_db.ping()
        if response:
            return 'Connection successful (Redis Local)'

    except redis.ConnectionError as e:
        logging.warning('Error connecting to redis(Local): %s'. str(e))
