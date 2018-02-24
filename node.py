from http.server import HTTPServer
from block import Block
from block.chain import Blockchain
from api.serve import APIHandler
from api.client import APIClient
import asyncio


app = APIHandler()


class NodeServerHandler():

    @app.when_get('/blocks')
    def list_blocks(self, params=None):
        chain = self.server.chain
        return 200, {'items': [item.to_dict() for item in chain]}

    @app.when_get('/blocks/last')
    def get_last_block(self, params=None):
        chain = self.server.chain
        last = chain.last()
        if last is None:
            return 404, {'error': 'blockchain is empty'}
        else:
            return 200, last.to_dict()

    @app.when_post('/blocks')
    def insert_block(self, data):
        try:
            new_block = Block(data.get('index'), data.get('previous_hash'), data.get('data'))
            self.server.chain.append(new_block)
            result_report = {"ok": True, "hash": new_block.hash}
            result_code = 200
        except Exception as error:
            result_report = {'error': error.message}
            result_code = 500
        return result_code, result_report

    @app.when_post('/peers')
    def add_peer(self, data):
        new_host = data.get('peer')
        if new_host not in [peer.host for peer in self.server.peers]:
            self.server.new_peer(new_host)
            return 201, {'ok': True}
        return 200, {'ok': True, 'known': True}


class NodeClient(APIClient):

    def __init__(self, host):
        # self.host = host
        # self.connect(host)
        super().__init__(host)

    async def update(self):
        print('updating', self, self.connection)
        status_code, result = self.get(url='/blocks')
        return status_code, result


class Node(HTTPServer):

    def __init__(self, port=8181, genesis_block=None):
        self.loop = asyncio.get_event_loop()
        self.port = port
        self.chain = Blockchain()
        if genesis_block is not None:
            self.chain.append(genesis_block)
        self.peers = []
        server_address = ('', port)
        super().__init__(server_address, app.serve)

    def new_peer(self, host):
        new_node = NodeClient(host)
        self.peers.append(new_node)
        self.loop.run_until_complete(new_node.update())

    def serve(self):
        try:
            self.serve_forever()
        finally:
            self.server_close()
        self.loop.close()

    @classmethod
    def run(cls, port=8181):
        return cls(port=port).serve()


if __name__ == '__main__':
    Node.run()
