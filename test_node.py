import unittest
from node import Node
import re
import threading
from api.client import APIClient


class BlockTestCase(unittest.TestCase, APIClient):

    def setUp(self):
        service = Node(port=5555)
        threading.Thread(target=service.serve).start()
        self.node = service
        self.connect('localhost:5555')

    def tearDown(self):
        self.node.shutdown()
        self.node.server_close()

    def test_simple_submit(self):
        block = {
            "index": 0,
            "previous_hash": "000000000",
            "data": {'text': 'This is a first test'}
        }
        status_code, result = self.post(url='/blocks', data=block)
        self.assertEqual(status_code, 200)
        self.assertEqual(result.get('ok'), True)

    def test_ok_to_append(self):
        block = {
            "index": 0,
            "previous_hash": "000000000",
            "data": {'text': 'This is a first test'}
        }
        status_code, result = self.post(url='/blocks', data=block)
        self.assertEqual(status_code, 200)
        self.assertEqual(result.get('ok'), True)
        block = {
            "index": 1,
            "previous_hash": result.get('hash'),
            "data": {'text': 'This is a second test'}
        }
        status_code, result = self.post(url='/blocks', data=block)
        self.assertEqual(status_code, 200)
        self.assertIn('ok', result)
        status_code, result = self.get(url='/blocks')
        self.assertEqual(status_code, 200)
        self.assertIn('items', result)
        self.assertEqual(len(result.get('items')), 2)
        status_code, result = self.get(url='/blocks', params={'from_index': 1})
        self.assertEqual(status_code, 200)
        self.assertEqual(len(result.get('items')), 2)

    def test_fails_to_append_by_hash(self):
        block = {
            "index": 0,
            "previous_hash": "000000000",
            "data": {'text': 'This is a first test'}
        }
        status_code, result = self.post(url='/blocks', data=block)
        self.assertEqual(status_code, 200)
        self.assertEqual(result.get('ok'), True)
        block = {
            "index": 1,
            "previous_hash": "000000000",
            "data": {'text': 'This is a second test'}
        }
        status_code, result = self.post(url='/blocks', data=block)
        self.assertEqual(status_code, 500)
        self.assertIn('error', result)
        expected_error = "Current hash \[[a-f0-9]*\] and \[[a-f0-9]*\] doesn't match."
        self.assertTrue(re.match(expected_error, result.get('error')))

    def test_fails_to_append_by_index(self):
        block = {
            "index": 0,
            "previous_hash": "000000000",
            "data": {'text': 'This is a first test'}
        }
        status_code, result = self.post(url='/blocks', data=block)
        self.assertEqual(status_code, 200)
        self.assertEqual(result.get('ok'), True)
        block = {
            "index": 2,
            "previous_hash": result.get('hash'),
            "data": {'text': 'This is a second test'}
        }
        status_code, result = self.post(url='/blocks', data=block)
        self.assertEqual(status_code, 500)
        self.assertIn('error', result)
        expected_error = "Blocks are not correlated.Index [0-9]+ was expected but received [0-9]+."
        self.assertTrue(re.match(expected_error, result.get('error')))

    def test_get_not_existent_last_block(self):
        status_code, result = self.get(url='/blocks/last')
        self.assertEqual(status_code, 404)

    def test_get_last_block(self):
        data = {'text': 'This is a first test'}
        block = {
            "index": 0,
            "previous_hash": "000000000",
            "data": data
        }
        status_code, result = self.post(url='/blocks', data=block)
        self.assertEqual(status_code, 200)
        self.assertEqual(result.get('ok'), True)
        status_code, result = self.get(url='/blocks/last')
        self.assertEqual(data, result.get('data'))

    def test_add_peer(self):
        self.assertEqual(len(self.node.peers), 0)
        new_peer = {'peer': 'ws://127.0.0.1:5556'}
        status_code, result = self.post(url='/peers', data=new_peer)
        self.assertEqual(status_code, 201)
        self.assertEqual(len(self.node.peers), 1)
        status_code, result = self.post(url='/peers', data=new_peer)
        self.assertEqual(status_code, 200)
        self.assertEqual(len(self.node.peers), 1)
