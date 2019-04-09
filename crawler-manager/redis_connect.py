import json
import logging
import redis
import os
import tempfile

logging.basicConfig(level=logging.INFO)

REDIS_HOST = os.environ.get('REDIS_HOST', 'crawler-redis')
redis_db = redis.Redis(host=REDIS_HOST, port=6379, db=0)

def get(key):
    return json.loads(redis_db.get(key))

def get_json(key):
    try:
        # logging.info("JSON! 333 %s", decode_value(redis_db.get(key), 'utf-8'))
        return json.loads(redis_db.get(key))
    except Exception as e:
        logging.info("Exception! %s", e)
        return None

def exists(key):
    return bool(redis_db.exists(key))

def put(key, value):
    logging.info('Putting %s: %s', key, value)
    return redis_db.set(key, json.dumps(value))

# TODO: these file writing functions should not be here
def write_crawler_csv(key=None):
    fd, path = tempfile.mkstemp()

    with os.fdopen(fd, 'w') as tmp:
        if key == None:
            tmp.write("")
        else:
            content = get_json(key)
            tmp.write('{}\n'.format(decode_value(content['s3_uri'], 'utf-8')))

            for url in content['child_urls']:
                tmp.write('{}\n'.format(decode_value(url, 'utf-8')))

            # logging.info("11 Writing %s to file", key)
            # logging.info("2 Writing %s to file", content['child_urls'])

    return path

def write_crawler_manifest(key=None):
    fd, path = tempfile.mkstemp()

    with os.fdopen(fd, 'w') as tmp:
        if key == None:
            tmp.write("")
        else:
            logging.info("11 Writing %s to file", key)
            # logging.info("2 Writing %s to file", content['child_urls'])
            tmp.write(json.dumps(get_json(key), indent=4))

    return path

# TODO: check if really deprecated, then delete it
def write_data_to_file():
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

def test_redis_connection():
    try:
        logging.info('Attempting to connect to Redis: ')
        logging.info(REDIS_HOST)

        response = redis_db.ping()
        if response:
            for key in redis_db.scan_iter("*"):
                logging.info('redis value %s --- %s', key, redis_db.get(key))

            return 'Connection successful (Redis Local)'

    except redis.ConnectionError as e:
        logging.warning('Error connecting to redis(Local): %s', str(e))
