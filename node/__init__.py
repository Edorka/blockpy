from block.chain import Blockchain
from .client import NodeClient
from .server import app
from api.server import APIServer


def majority(hashes_and_peers):
    """Will return the hash and first member of the most populated choice
    on the input
    :param:hashes_and_peers dict of hashed referencing a list of the peers
    which have replied with sush hash of last block on their chains"""
    if len(hashes_and_peers) == 0:
        return None, None
    if len(hashes_and_peers) == 1:
        return hashes_and_peers[0]
    return choose_majority(hashes_and_peers)


def accumulate_members(current_hash, peer, peers_for_hash):
    previous_hash_members = peers_for_hash.get(current_hash, [])
    current_hash_members = previous_hash_members + [peer]
    peers_for_hash[current_hash] = current_hash_members
    return current_hash_members


def choose_majority(hashes_and_peers):
    peers_for_hash = {}
    best_hash = None
    best_hash_members_count = 0
    for current_hash, peer in hashes_and_peers:
        current_hash_members = accumulate_members(current_hash, peer, peers_for_hash)
        current_hash_members_count = len(current_hash_members)
        if current_hash_members_count > best_hash_members_count:
            best_hash = current_hash
            best_hash_members_count = current_hash_members_count
    return best_hash, peers_for_hash[best_hash].pop()


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
        for host in peers:
            self.add_peer(host)

    def add_peer(self, host):
        new_node = NodeClient(host)
        self.peers.append(new_node)
        return new_node

    def new_peer(self, host):
        new_node = self.add_peer(host)
        new_node.get_update(self.chain)

    def find_best_peer(self, last_index=0):
        best_peers = []
        for peer in self.peers:
            last_block = peer.get_last_block()
            if last_block is None:
                continue
            node_last_index = last_block.index
            peer_tuple = (last_block.hash, peer)
            if node_last_index > last_index:
                last_index = node_last_index
                best_peers = [peer_tuple]
            else:
                best_peers.append(peer_tuple)
                pass  # ignored
        _, result = majority(best_peers)
        return result

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
