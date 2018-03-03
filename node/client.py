from api.client import APIClient
from block import Block, GenesisBlock
from collections import deque


def block_from_data(source):
    index = source.get('index')
    if index == 0:
        return GenesisBlock(source.get('data'),
                            source.get('timestamp'))
    return Block(index,
                 source.get('previous_hash'),
                 source.get('data'),
                 source.get('timestamp'))


class NodeClient(APIClient):

    def __init__(self, host):
        self.errors = deque()
        super().__init__(host)

    def update_with_data(self, response, current):
        for data in response.get('items', []):
            try:
                new_block = block_from_data(data)
                current.append(new_block)
            except Exception as error:
                self.errors.append(error)

    def get_last_block(self, last_known=0):
        status_code, result = self.get(url='/blocks/last')
        if status_code == 200:
            index = result.get('index')
            if index > last_known:
                last_block = block_from_data(result)
                return last_block
        return None

    def get_update(self, current):
        processed_index = max([block.index for block in current])
        index_param = {'from_index': processed_index + 1}
        status_code, result = self.get(url='/blocks', params=index_param)
        if status_code == 200:
            self.update_with_data(result, current)

    def report_update(self, new_block):
        try:
            return self.put(url='/blocks', data=new_block.to_dict())
        except Exception as error:
            self.errors.append(error)
            return error
