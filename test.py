import unittest
from block import Block
from block.exceptions import (BlocksNotCorrelativeException,
                              BlocksNotSequentialException,
                              BlockHashDontMatchException)


class BlockTestCase(unittest.TestCase):

    def test_genesis_valid_next(self):
        data = {
            'message': 'this is the genesis block'
        }
        genesis_block = Block(0, "000", data)
        data = {
            'message': 'this is a test'
        }
        next_block = genesis_block.next(data)
        self.assertTrue(genesis_block.verify_next(next_block))

    def test_invalid_index(self):
        data = {
            'message': 'this is the genesis block'
        }
        genesis_block = Block(0, "000", data)
        data = {
            'message': 'this is a test'
        }
        next_block = genesis_block.next(data)
        next_block.timestamp = genesis_block.timestamp + 100
        genesis_block.index = 5
        with self.assertRaises(BlocksNotCorrelativeException):
            genesis_block.verify_next(next_block)

    def test_invalid_timestamp(self):
        data = {
            'message': 'this is the genesis block'
        }
        genesis_block = Block(0, "000", data)
        data = {
            'message': 'this is a test'
        }
        next_block = genesis_block.next(data)
        next_block.timestamp = genesis_block.timestamp - 100
        with self.assertRaises(BlocksNotSequentialException):
            genesis_block.verify_next(next_block)

    def test_invalid_hash(self):
        data = {
            'message': 'this is the genesis block'
        }
        genesis_block = Block(0, "000", data)
        data = {
            'message': 'this is a test'
        }
        next_block = genesis_block.next(data)
        next_block.timestamp = genesis_block.timestamp + 100
        genesis_block.data = {
            'message': 'this is a modified genesis block'
        }
        with self.assertRaises(BlockHashDontMatchException):
            genesis_block.verify_next(next_block)


if __name__ == "__main__":
    unittest.main()
