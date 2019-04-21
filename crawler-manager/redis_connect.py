import json
import logging
import redis
import os
import tempfile

logging.basicConfig(level=logging.INFO)

# crawler manager uses it's own local redis
REDIS_HOST = os.environ.get('REDIS_HOST', '0.0.0.0')
redis_db = redis.Redis(host=REDIS_HOST, port=6379, db=0)


def get(key):
    return json.loads(redis_db.get(key))


def exists(key):
    return bool(redis_db.exists(key))


def put(key, value):
    return redis_db.set(key, json.dumps(value))


def write_manifest():
    fd, path = tempfile.mkstemp()
    with os.fdopen(fd, 'w') as tmp:
        keys = redis_db.keys()
        for key in keys:
            value = redis_db.get(key)
            record = '{},{},\n'.format(decode_value(key, 'utf-8'), decode_value(value, "utf-8"))
            logging.info("Writing %s to file", record)
            tmp.write(record)

    return path

def decode_value(val, charset):
    try:
        return val.decode(charset)
    except Exception as e:
        return val

def dump():
    for key in redis_db.scan_iter("*"):
        logging.info('redis value %s --- %s', key, redis_db.get(key))
    

def test_redis_connection():
    try:
        logging.info('Attempting to connect to Redis: ')
        logging.info(REDIS_HOST)
        response = redis_db.ping()

    except redis.ConnectionError as e:
        logging.warning('Error connecting to redis(Local): %s', str(e))
