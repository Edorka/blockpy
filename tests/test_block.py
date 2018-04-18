import unittest
from unittest import mock
from block import Block
import datetime
import hashlib
import json


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
        selected_datetime = datetime.datetime(2018, 3, 1, 11, 21, 33)
        with mock.patch('datetime.datetime') as mock_datetime:
            mock_datetime.today.return_value = default_datetime
            block = Block(0, '000000000', {'message': 'do not panic'},
                          timestamp=selected_datetime.timestamp())
            expected = selected_datetime.timestamp()
            self.assertEqual(block.timestamp, expected)

    @mock.patch.object(hashlib, 'sha256')
    def test_obtained_hash(self, mocked):
        selected_datetime = datetime.datetime(2018, 3, 1, 11, 21, 33)
        index = 0
        previous_hash = '000000000'
        selected_timestamp = selected_datetime.timestamp()
        content = {'message': 'do not panic'}
        Block(index, previous_hash, content, selected_timestamp)
        [hash_input], kwargs = mocked.call_args
        obtained = hash_input.decode()
        self.assertIn(str(index), obtained)
        self.assertIn(str(previous_hash), obtained)
        self.assertIn(str(selected_timestamp), obtained)
        self.assertIn(json.dumps(content), obtained)

    def test_is_equal(self):
        selected_datetime = datetime.datetime(2018, 3, 1, 11, 21, 33)
        index = 0
        previous_hash = '000000000'
        selected_timestamp = selected_datetime.timestamp()
        content = {'message': 'do not panic'}
        one_block = Block(index, previous_hash, content, selected_timestamp)
        equal_block = Block(index, previous_hash, content, selected_timestamp)
        self.assertTrue(one_block == equal_block)

    def test_is_not_equal_by_index(self):
        selected_datetime = datetime.datetime(2018, 3, 1, 11, 21, 33)
        index = 0
        previous_hash = '000000000'
        selected_timestamp = selected_datetime.timestamp()
        content = {'message': 'do not panic'}
        one_block = Block(index, previous_hash, content, selected_timestamp)
        other_index = 1
        other_block = Block(other_index, previous_hash, content, selected_timestamp)
        self.assertTrue(one_block != other_block)

    def test_is_not_equal_by_previous_hash(self):
        selected_datetime = datetime.datetime(2018, 3, 1, 11, 21, 33)
        index = 0
        previous_hash = '000000000'
        selected_timestamp = selected_datetime.timestamp()
        content = {'message': 'do not panic'}
        one_block = Block(index, previous_hash, content, selected_timestamp)
        other_previous_hash = '3a3a3a3a33a'
        other_block = Block(index, other_previous_hash, content, selected_timestamp)
        self.assertTrue(one_block != other_block)

    def test_is_not_equal_by_timestamp(self):
        selected_datetime = datetime.datetime(2018, 3, 1, 11, 21, 33)
        index = 0
        previous_hash = '000000000'
        selected_timestamp = selected_datetime.timestamp()
        content = {'message': 'do not panic'}
        one_block = Block(index, previous_hash, content, selected_timestamp)
        other_datetime = datetime.datetime(2018, 3, 1, 11, 21, 32)
        other_timestamp = other_datetime.timestamp()
        other_block = Block(index, previous_hash, content, other_timestamp)
        self.assertTrue(one_block != other_block)

    def test_is_not_equal_by_content(self):
        selected_datetime = datetime.datetime(2018, 3, 1, 11, 21, 33)
        index = 0
        previous_hash = '000000000'
        selected_timestamp = selected_datetime.timestamp()
        content = {'message': 'do not panic'}
        one_block = Block(index, previous_hash, content, selected_timestamp)
        other_content = {
            'message': 'do not panic',
            'additional': 'this is not expected'
        }
        other_block = Block(index, previous_hash, other_content, selected_datetime)
        self.assertTrue(one_block != other_block)

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
