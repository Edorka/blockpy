from . import Node
from block import GenesisBlock
from os import environ
 
data = {
    'message': 'this is the genesis block'
}
genesis_block = GenesisBlock(data)
try:
    port = int(environ.get('PORT', None))
except ValueError:
    port = 80
Node(port=port, genesis_block=genesis_block).serve()
