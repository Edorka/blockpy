import unittest
from node import Node
import threading
from api.client import APIClient
from block import GenesisBlock


class BlockTestCase(unittest.TestCase, APIClient):

    def setUp(self):
        data = {
            'message': 'this is the genesis block'
        }
        genesis_block = GenesisBlock(data)
        service_a = Node(port=5555, genesis_block=genesis_block)
        service_b = Node(port=5556, genesis_block=genesis_block)
        threading.Thread(target=service_a.serve).start()
        threading.Thread(target=service_b.serve).start()
        self.node_a = service_a
        self.node_b = service_b
        self.genesis_block = genesis_block

    def tearDown(self):
        self.node_a.shutdown()
        self.node_a.server_close()
        self.node_b.shutdown()
        self.node_b.server_close()

    def test_peer_would_import_node_a(self):
        new_block = self.genesis_block.next({"message": "second block"})
        self.node_a.chain.append(new_block)
        service_c = Node(port=5558, genesis_block=self.genesis_block, peers=['127.0.0.1:5555'])
        self.assertEqual(len(service_c.peers), 1)
        self.assertEqual(len(service_c.chain), 2)
        service_c.server_close()

    def test_peer_cant_import_diffrent_network(self):
        new_block = self.genesis_block.next({"message": "second block"})
        self.node_a.chain.append(new_block)
        data = {
            'message': 'this is the genesis block'
        }
        rogue_genesis_work = GenesisBlock(data)
        service_c = Node(port=5558, genesis_block=rogue_genesis_work, peers=['127.0.0.1:5555'])
        self.assertEqual(len(service_c.peers), 1)
        self.assertEqual(len(service_c.chain), 1)
        service_c.server_close()


