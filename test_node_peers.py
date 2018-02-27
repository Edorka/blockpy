import unittest
from node import Node, NodeClient
import threading
from api.client import APIClient
from block import GenesisBlock


class BlockTestCase(unittest.TestCase, APIClient):

    def setUp(self):
        data = {
            'message': 'this is the genesis block'
        }
        genesis_block = GenesisBlock(data)
        service_a = Node(port=35555, genesis_block=genesis_block)
        service_b = Node(port=35556, genesis_block=genesis_block)
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
        service_c = Node(port=35558, genesis_block=self.genesis_block, peers=['localhost:35555'])
        self.assertEqual(len(service_c.peers), 1)
        self.assertEqual(len(service_c.chain), 2)
        service_c.server_close()

    def test_peer_cant_import_different_network(self):
        new_block = self.genesis_block.next({"message": "second block"})
        self.node_a.chain.append(new_block)
        self.assertEqual(len(self.node_a.chain), 2)
        data = {
            'message': 'this is not the same genesis block'
        }
        rogue_genesis_work = GenesisBlock(data)
        service_c = Node(port=35558, genesis_block=rogue_genesis_work, peers=['localhost:35555'])
        self.assertEqual(len(service_c.peers), 1)
        self.assertEqual(len(service_c.chain), 1)
        service_c.server_close()

    def test_peer_can_update_other_nodes(self):
        new_block = self.genesis_block.next({"message": "second block"})
        peers = ['localhost:35555', 'localhost:35556']
        service_c = Node(port=35558, genesis_block=self.genesis_block, peers=peers)
        threading.Thread(target=service_c.serve).start()
        client_to_c = NodeClient('localhost:35558')
        status_code, result = client_to_c.report(new_block)
        # status_code, result = self.post(url='/blocks', data=new_block.to_dict())
        # print(status_code, result)
        self.assertEqual(len(service_c.peers), 2)
        self.assertEqual(len(self.node_a.chain), 2)
        self.assertEqual(len(self.node_b.chain), 2)
        service_c.shutdown()
        service_c.server_close()
