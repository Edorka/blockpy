from collections import deque


class Blockchain(deque):

    def last(self):
        if len(self) == 0:
            return None
        return self[-1]

    def append(self, other):
        last = self.last()
        if last is not None:
            last.verify_next(other)
        super().append(other)
