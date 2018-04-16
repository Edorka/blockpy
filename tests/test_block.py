import unittest
from unittest import mock
from block import Block
import datetime


class BlockTestCase(unittest.TestCase):

    def test_index_attribute(self):
        block = Block(0, '000000000', {'message': 'do not panic'})
        self.assertEqual(block.index, 0)

    def test_data_attribute(self):
        expected = {'message': 'do not panic'}
        block = Block(0, '000000000', {'message': 'do not panic'})
        self.assertEqual(block.data, expected)

    def test_timestamp_as_none_attribute(self):
        fixed_datetime = datetime.datetime(2010, 1, 1, 10, 20, 30)
        with mock.patch('datetime.datetime') as mock_datetime:
            mock_datetime.today.return_value = fixed_datetime
            block = Block(0, '000000000', {'message': 'do not panic'})
            expected = fixed_datetime.timestamp()
            self.assertEqual(block.timestamp, expected)

    def test_timestamp_as_attribute(self):
        default_datetime = datetime.datetime(2010, 1, 1, 10, 20, 30)
        selected_datetime = datetime.datetime(2018, 3, 1, 10, 20, 30)
        with mock.patch('datetime.datetime') as mock_datetime:
            mock_datetime.today.return_value = default_datetime
            block = Block(0, '000000000', {'message': 'do not panic'},
                          timestamp=selected_datetime.timestamp())
            expected = selected_datetime.timestamp()
            self.assertEqual(block.timestamp, expected)

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


if __name__ == "__main__":
    unittest.main()
