import unittest
from node import Node
import threading
from api.client import APIClient


class BlockTestCase(unittest.TestCase):

    def setUp(self):
        service_a = Node(port=5555)
        service_b = Node(port=5556)
        threading.Thread(target=service_a.serve).start()
        threading.Thread(target=service_b.serve).start()
        self.node_a = service_a
        self.node_b = service_b

    def tearDown(self):
        self.node_a.shutdown()
        self.node_a.server_close()
        self.node_b.shutdown()
        self.node_b.server_close()

    def test_add_peer(self):
        client_to_a = APIClient('localhost:5555')
        client_to_a.post('/peers', data={'peer': 'localhost:5556'})
        self.assertFalse(True)
