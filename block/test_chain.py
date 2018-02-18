import unittest
from block.chain import Blockchain
from block import Block
from block.exceptions import (BlocksNotCorrelativeException,
                              BlocksNotSequentialException,
                              BlockHashDontMatchException)


class BlockTestCase(unittest.TestCase):

    def test_adding_blocks(self):
        chain = Blockchain()
        data = {
            'message': 'this is the genesis block'
        }
        genesis_block = Block(0, "000", data)
        data = {
            'message': 'this is a test'
        }
        chain.append(genesis_block)
        next_block = Block(1, "000", data)
        next_block.timestamp = genesis_block.timestamp + 100
        next_block.data = {
            'message': 'this is a modified genesis block'
        }
        with self.assertRaises(BlockHashDontMatchException):
            chain.append(next_block)
        next_block.previous_hash = genesis_block.hash
        chain.append(next_block)
        self.assertIn(next_block, chain)
        self.assertIn(genesis_block, chain)
