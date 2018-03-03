from block.chain import Blockchain
from .client import NodeClient
from .server import app
from api.server import APIServer


class Node(APIServer):

    def __init__(self, genesis_block=None, peers=[], **kwargs):
        self.set_chain(genesis_block)
        self.set_peers(peers)
        self.update_from_peers()
        super().__init__(app, **kwargs)

    def set_chain(self, genesis_block):
        self.chain = Blockchain()
        if genesis_block is not None:
            self.chain.append(genesis_block)

    def add_block(self, new_block, report=False):
        if new_block in self.chain:
            return False
        self.chain.append(new_block)
        if report is True:
            self.broadcast(new_block)
        return True

    def set_peers(self, peers):
        self.peers = []
        for peer in peers:
            self.new_peer(peer)

    def new_peer(self, host):
        new_node = NodeClient(host)
        self.peers.append(new_node)
        new_node.get_update(self.chain)

    def find_best_peer(self, last_index=0):
        best_peer = None
        for peer in self.peers:
            last_block = peer.get_last_block(last_index)
            if last_block is None:
                continue
            node_last_index = last_block.index
            if node_last_index > last_index:
                last_index, best_peer = node_last_index, peer
        return best_peer

    def update_from_peers(self):
        last_index = max([block.index for block in self.chain])
        best_peer = self.find_best_peer(last_index)
        if best_peer is not None:
            best_peer.get_update(self.chain)

    def broadcast(self, new_block):
        for peer in self.peers:
            peer.report_update(new_block)

    @classmethod
    def run(cls, port=8181):
        return cls(port=port).serve()


if __name__ == '__main__':
    Node.run()
