class BlocksNotCorrelativeException(Exception):
    _message = 'Blocks are not correlated.Index {} was expected but received {}.'

    def __init__(self, expected, received):
        message = self.__class__._message.format(expected, received)
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
        self.message = message


class BlocksNotSequentialException(Exception):
    _message = 'Timestamp {} was expeted to be after {}.'

    def __init__(self, timestamp, next_timestamp):
        message = self.__class__._message.format(next_timestamp, timestamp)
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
        self.message = message


class BlockHashDontMatchException(Exception):
    _message = "Current hash [{}] and [{}] doesn't match."

    def __init__(self, current_hash, refences_hash):
        message = self.__class__._message.format(current_hash, refences_hash)
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
        self.message = message
