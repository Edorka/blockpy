import unittest
from node import Node
import http.client
import re
import json
import threading


class BlockTestCase(unittest.TestCase):

    def setUp(self):
        service = Node(port=5555)
        threading.Thread(target=service.serve).start()
        self.node = service
        self.connection = http.client.HTTPConnection('localhost:5555')

    def tearDown(self):
        self.node.shutdown()

    def post(self, url='/', data={}):
        headers = {'Content-type': 'application/json'}
        json_str = json.dumps(data)
        self.connection.request('POST', url, json_str, headers)
        response = self.connection.getresponse()
        result = json.loads(response.read().decode('utf-8'))
        return response.status, result

    def get(self, url='/'):
        headers = {'Content-type': 'application/json'}
        self.connection.request('GET', url, "", headers)
        response = self.connection.getresponse()
        result = json.loads(response.read().decode('utf-8'))
        return response.status, result

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
