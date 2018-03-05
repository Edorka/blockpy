import unittest
from node import Node
import threading
from api.client import APIClient
from block import GenesisBlock


class PeersTestCase(unittest.TestCase, APIClient):

    def create_node(self, name, port=35555, genesis_block=None, peers=[]):
        if genesis_block is None:
            genesis_block = self.genesis_block
        if name in self.nodes:
            raise Exception('{} node already exists'.format(name))
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
        peer_list = ','.join(self.nodes.keys())
        print('shutting down: {}'.format(peer_list))
        for name, node in self.nodes.items():
            node.shutdown()
            node.server_close()

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

    def test_peer_address_collision(self):
        import socket
        with self.assertRaises(socket.error):
            self.create_node('c', port=35555)

    def test_update_from_longest_chain(self):
        last = self.genesis_block
        node_a = self.nodes.get('a')
        node_b = self.nodes.get('b')
        for current in range(5):
            new_block = last.next({"message": "new block:{}".format(current)})
            if current < 4:
                node_a.add_block(new_block)
            node_b.add_block(new_block)
            last = new_block
        peers = ['localhost:35555', 'localhost:35556']
        node_c = self.create_node('c', port=35558,
                                  peers=peers)
        self.assertEqual(len(node_c.chain), 6)

    def test_do_not_update_from_discrepant(self):
        node_a = self.nodes.get('a')
        node_b = self.nodes.get('b')
        node_c = self.create_node('c', port=45557)
        node_d = self.create_node('d', port=45558)
        last = self.genesis_block
        for current in range(5):
            new_block = last.next({"message": "new block:{}".format(current)})
            node_b.add_block(new_block)
            node_c.add_block(new_block)
            node_d.add_block(new_block)
            if current < 4:
                node_a.add_block(new_block)
            else:
                rare_block = last.next({"message": "rare block:{}".format(current)})
                node_a.add_block(rare_block)
            last = new_block
        self.assertEqual(len(node_a.chain), 6)
        self.assertEqual(len(node_b.chain), 6)
        self.assertEqual(len(node_c.chain), 6)
        self.assertEqual(len(node_d.chain), 6)
        peers = ['localhost:35555',
                 'localhost:35556',
                 'localhost:45557',
                 'localhost:45558']
        node_n = self.create_node('n', port=45559,
                                  peers=peers)
        self.assertEqual(len(node_n.peers), 4)
        self.assertEqual(len(node_n.chain), 6)
        last_node = node_n.chain.last()
        self.assertEqual(last_node.hash, last.hash)
