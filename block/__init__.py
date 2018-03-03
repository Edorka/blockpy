from datetime import datetime
import hashlib
import json


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
        return Block(index, self.hash, data, timestamp)

    def to_dict(self):
        return {
            'index': self.index,
            'previous_hash': self.previous_hash,
            'timestamp': self.timestamp,
            'data': self.data,
            'hash': self.hash
        }

    def __eq__(self, other):
        return (self.index == other.index and
                self.data == other.data and
                self.timestamp == other.timestamp and
                self.hash == other.hash and
                self.previous_hash == other.previous_hash)

    def __repr__(self):
        return "<Block {index} {hash} {timestamp}>".format(index=self.index,
                                                           hash=self.hash,
                                                           timestamp=self.timestamp)


class GenesisBlock(Block):

    def __init__(self, data, timestamp=None):
        index = 0
        previous_hash = None
        super().__init__(index, previous_hash, data, timestamp=timestamp)

    def get_hash(self):
        content = str(self.index) + str(self.timestamp)
        content += json.dumps(self.data)
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def to_dict(self):
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'data': self.data,
            'hash': self.hash
        }
