import unittest
from node import Node, NodeClient
import threading
from api.client import APIClient
from block import GenesisBlock


class BlockTestCase(unittest.TestCase, APIClient):

    def create_node(self, name, port=35555, genesis_block=None, peers=[]):
        print('creating', name, port)
        if genesis_block is None:
            genesis_block = self.genesis_block
        new_node = Node(port=port, peers=peers, genesis_block=genesis_block)
        self.nodes[name] = new_node
        threading.Thread(target=new_node.serve).start()
        return new_node

    def setUp(self):
        self.nodes = {}
        data = {
            'message': 'this is the genesis block'
        }
        self.genesis_block = GenesisBlock(data)
        self.create_node('a', port=35555)
        self.create_node('b', port=35556)

    def tearDown(self):
        for name, node in self.nodes.items():
            node.shutdown()
            node.server_close()
            print('closing', name, node)

    def test_peer_would_import_node_a(self):
        new_block = self.genesis_block.next({"message": "second block"})
        node_a = self.nodes.get('a')
        node_a.chain.append(new_block)
        node_c = self.create_node('c', port=35558, peers=['localhost:35555'])
        self.assertEqual(len(node_c.peers), 1)
        self.assertEqual(len(node_c.chain), 2)

    def test_peer_cant_import_different_network(self):
        new_block = self.genesis_block.next({"message": "second block"})
        node_a = self.nodes.get('a')
        node_a.chain.append(new_block)
        self.assertEqual(len(node_a.chain), 2)
        data = {
            'message': 'this is not the same genesis block'
        }
        rogue_genesis_work = GenesisBlock(data)
        node_c = self.create_node('c', port=35558,
                                  genesis_block=rogue_genesis_work,
                                  peers=['localhost:35555'])
        self.assertEqual(len(node_c.peers), 1)
        self.assertEqual(len(node_c.chain), 1)

    def test_peer_can_update_other_nodes(self):
        new_block = self.genesis_block.next({"message": "second block"})
        peers = ['localhost:35555', 'localhost:35556']
        node_c = self.create_node('c', port=35558,
                                  peers=peers)
        node_c.add_block(new_block, report=True)
        node_a = self.nodes.get('a')
        node_b = self.nodes.get('b')
        self.assertEqual(len(node_c.peers), 2)
        self.assertEqual(len(node_a.chain), 2)
        self.assertEqual(len(node_b.chain), 2)
