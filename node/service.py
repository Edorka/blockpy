from block import Block
from api.serve import APIHandler


app = APIHandler()


class NodeServerHandler():

    @app.when_get('/blocks')
    def list_blocks(self, params=None):
        chain = self.server.chain
        index_start = 0
        if isinstance(params, dict):
            index_start_values = params.get('from_index')
            if type(index_start_values) == list:
                index_start = int(index_start_values[0])
        items = [item.to_dict() for item in chain if item.index >= index_start]
        return 200, {'items': items}

    @app.when_get('/blocks/last')
    def get_last_block(self, params=None):
        chain = self.server.chain
        last = chain.last()
        if last is None:
            return 404, {'error': 'blockchain is empty'}
        else:
            return 200, last.to_dict()

    @app.when_put('/blocks')
    def update_blocks(self, data):
        result_code = 200
        result_report = {'result': 'unknown'}
        try:
            new_block = Block(data.get('index'),
                              data.get('previous_hash'),
                              data.get('data'),
                              data.get('timestamp'))
            is_new = self.server.add_block(new_block, report=False)
            result_code = 201 if is_new else 200
            result_report = {"ok": True, "hash": new_block.hash}
        except Exception as error:
            result_report = {'error': error.message}
            result_code = 500
        return result_code, result_report

    @app.when_post('/blocks')
    def admit_block(self, data):
        result_code = 201
        result_report = {'result': 'unkown'}
        try:
            new_block = Block(data.get('index'), data.get('previous_hash'), data.get('data'))
            self.server.add_block(new_block, report=True)
            result_report = {"ok": True, "hash": new_block.hash}
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
