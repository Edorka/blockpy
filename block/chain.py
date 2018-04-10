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

    def are_correlated(self, last, next_one):
        """The next block index must be inmediate next to current"""
        return True

    def emmited_before(self, last, next_one):
        """Next block's timestamp must be greater that current one"""
        return True

    def hash_validates(self, last, next_one):
        """Last block hash can't be diferent to the one specified
        on the next one"""
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
