import unittest
from block import Block
from block.chain import Blockchain
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
        self.assertEqual(next_block.previous_hash, genesis_block.hash)


class BlockchainTestCase(unittest.TestCase):

    def setUp(self):
        self.chain = Blockchain()

    def test_adding_blocks(self):
        data = {
            'message': 'this is the genesis block'
        }
        genesis_block = Block(0, "000", data)
        data = {
            'message': 'this is a test'
        }
        self.chain.append(genesis_block)
        next_block = Block(1, "000", data)
        next_block.timestamp = genesis_block.timestamp + 100
        next_block.data = {
            'message': 'this is a modified genesis block'
        }
        with self.assertRaises(BlockHashDontMatchException):
            self.chain.append(next_block)
        next_block.previous_hash = genesis_block.hash
        self.chain.append(next_block)
        self.assertIn(next_block, self.chain)
        self.assertIn(genesis_block, self.chain)

    def test_invalid_index(self):
        data = {
            'message': 'this is the genesis block'
        }
        genesis_block = Block(0, "000", data)
        self.chain.append(genesis_block)
        data = {
            'message': 'this is a test'
        }
        next_block = genesis_block.next(data)
        next_block.timestamp = genesis_block.timestamp + 100
        genesis_block.index = 5
        with self.assertRaises(BlocksNotCorrelativeException):
            self.chain.append(next_block)

    def test_invalid_timestamp(self):
        data = {
            'message': 'this is the genesis block'
        }
        genesis_block = Block(0, "000", data)
        self.chain.append(genesis_block)
        data = {
            'message': 'this is a test'
        }
        next_block = genesis_block.next(data)
        next_block.timestamp = genesis_block.timestamp - 100
        with self.assertRaises(BlocksNotSequentialException):
            self.chain.append(next_block)

    def test_invalid_hash(self):
        data = {
            'message': 'this is the genesis block'
        }
        genesis_block = Block(0, "000", data)
        self.chain.append(genesis_block)
        data = {
            'message': 'this is a test'
        }
        next_block = genesis_block.next(data)
        next_block.timestamp = genesis_block.timestamp + 100
        genesis_block.data = {
            'message': 'this is a modified genesis block'
        }
        with self.assertRaises(BlockHashDontMatchException):
            self.chain.append(next_block)


if __name__ == "__main__":
    unittest.main()
