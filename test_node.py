import unittest
from node import Node
import http.client
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

    def test_simple_submit(self):
        headers = {'Content-type': 'application/json'}
        block = {
            "index": 0,
            "previous_hash": "000000000",
            "data": {'text': 'Hello world github/linguist#1 **cool**, and #1!'}
        }
        json_block = json.dumps(block)
        self.connection.request('POST', '/', json_block, headers)
        response = self.connection.getresponse()
        result = json.loads(response.read().decode('utf-8'))
        self.assertEqual(result.get('ok'), True)
