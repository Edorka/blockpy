from collections import deque
from block import GenesisBlock
from block.exceptions import (BlocksNotCorrelativeException,
                              BlocksNotSequentialException,
                              BlockHashDontMatchException,
                              FirstGenesisBlockExpectedException)


class Blockchain(deque):

    def last(self):
        if len(self) == 0:
            return None
        return self[-1]

    def are_correlated(self, one, other):
        received = other.index
        expected = one.index + 1
        if received != expected:
            raise BlocksNotCorrelativeException(received, expected)
        return True

    def emmited_before(self, one, other):
        next_timestamp = other.timestamp
        timestamp = one.timestamp
        if next_timestamp < timestamp:
            raise BlocksNotSequentialException(timestamp, next_timestamp)
        return True

    def hash_validates(self, one, other):
        refences_hash = other.previous_hash
        current_hash = one.get_hash()
        if refences_hash != current_hash:
            raise BlockHashDontMatchException(current_hash, refences_hash)
        return True

    def validate_next(self, last, next_block):
        self.are_correlated(last, next_block)
        self.emmited_before(last, next_block)
        self.hash_validates(last, next_block)
        return True

    def append(self, other):
        last = self.last()
        if last is None:
            if isinstance(other, GenesisBlock) is not True:
                raise FirstGenesisBlockExpectedException(received=other)
        else:
            self.validate_next(last, other)
        super().append(other)
