import json
import logging
import redis
import os
import tempfile

logging.basicConfig(level=logging.INFO)


class RedisClient:
    def __init__(self, conn):
        self.conn = conn

    def dump(self):
        for key in self.conn.scan_iter("*"):
            logging.info('%s -> %s', key.decode(), self.conn.get(key).decode())

    def exists(self, key):
        return bool(self.conn.exists(key.encode()))


    def get(self, key):
        return json.loads(self.conn.get(key.encode()).decode())
    
    def ping(self):
        self.conn.ping()

    def put(self, key, value):
        return self.conn.set(key.encode(), json.dumps(value).encode())
    
    def write_manifest(self):
        fd, path = tempfile.mkstemp()
        with os.fdopen(fd, 'w') as tmp:
            keys = self.conn.keys()
            for key in keys:
                value = self.conn.get(key)
                record = '{},{},\n'.format(key.decode(), json.loads(value.decode()))
                logging.info("Writing %s to file", record)
                tmp.write(record)

        return path

    def reset(self):
        keys = self.conn.keys()
        for key in keys:
            self.conn.delete(key)
