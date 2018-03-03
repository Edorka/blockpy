from api.client import APIClient
from block import Block
from collections import deque


class NodeClient(APIClient):

    def __init__(self, host):
        self.errors = deque()
        super().__init__(host)

    def update_with_data(self, response, current):
        for data in response.get('items', []):
            try:
                index = data.get('index')
                new_block = Block(index, data.get('previous_hash'), data.get('data'))
                current.append(new_block)
            except Exception as error:
                self.errors.append(error)

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
