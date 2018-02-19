from datetime import datetime
import hashlib
import json
from .exceptions import (BlocksNotCorrelativeException,
                         BlocksNotSequentialException,
                         BlockHashDontMatchException)


def current_timestamp():
    now = datetime.today()
    return now.timestamp()


class Block:

    def __init__(self, index, previous_hash, data, timestamp=None):
        self.index = index
        self.previous_hash = previous_hash
        if timestamp is None:
            timestamp = current_timestamp()
        self.timestamp = timestamp
        self.data = data
        self.hash = self.get_hash()

    def get_hash(self):
        content = str(self.index) + self.previous_hash + str(self.timestamp)
        content += json.dumps(self.data)
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def next(self, data, index=None,  timestamp=None):
        timestamp = current_timestamp() if timestamp is None else timestamp
        index = self.index + 1 if index is None else index
        return self.__class__(index, self.hash, data, timestamp)
