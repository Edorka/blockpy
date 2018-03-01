from block.chain import Blockchain
from .service import app
from .client import NodeClient
import socket
from http.server import HTTPServer


class Node(HTTPServer):
    allow_reuse_address = True

    def __init__(self, port=8181, genesis_block=None, peers=[]):
        self.set_chain(genesis_block)
        self.listen(port)
        self.set_peers(peers)
        self.update_from_peers()

    def set_chain(self, genesis_block):
        self.chain = Blockchain()
        if genesis_block is not None:
            self.chain.append(genesis_block)

    def add_block(self, new_block, report=False):
        self.chain.append(new_block)
        if report is True:
            self.broadcast(new_block)

    def listen(self, port, retry=3):
        while retry:
            try:
                server_address = ('', port)
                super().__init__(server_address, app.serve)
                break
            except socket.error as error:
                retry -= 1
                if retry is 0:
                    raise error

    def serve(self):
        try:
            self.serve_forever()
        finally:
            self.server_close()

    def set_peers(self, peers):
        self.peers = []
        for peer in peers:
            self.new_peer(peer)

    def new_peer(self, host):
        new_node = NodeClient(host)
        self.peers.append(new_node)
        new_node.update(self.chain)

    def update_from_peers(self):
        for peer in self.peers:
            peer.update(self.chain)

    def broadcast(self, new_block):
        for peer in self.peers:
            peer.report(new_block)

    @classmethod
    def run(cls, port=8181):
        return cls(port=port).serve()


if __name__ == '__main__':
    Node.run()
