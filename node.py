from http.server import BaseHTTPRequestHandler, HTTPServer
from block import Block
from block.chain import Blockchain
import json
from json.decoder import JSONDecodeError


class NodeServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        chain = self.server.chain
        result = {'items': [item.to_dict() for item in chain]}
        self.end_headers()
        json_string = json.dumps(result)
        self.wfile.write(json_string.encode('utf-8'))

    def extract_json(self):
        content_len = int(self.headers.get('content-length'))
        post_body = self.rfile.read(content_len)
        return json.loads(post_body.decode('utf-8'))

    def reply_json(self, data, status_code=200):
        json_string = json.dumps(data)
        self.send_response(status_code)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json_string.encode('utf-8'))

    def insert_block(self, json):
        result_code = 200
        try:
            new_block = Block(json.get('index'), json.get('previous_hash'), json.get('data'))
            self.server.chain.append(new_block)
            result_report = {"ok": True, "hash": new_block.hash}
        except Exception as error:
            result_report = {'error': error.message}
            result_code = 500
        return result_code, result_report

    def do_POST(self):
        try:
            json = self.extract_json()
            result_code, result_report = self.insert_block(json)
            self.reply_json(result_report, result_code)
        except JSONDecodeError as error:
            self.reply_json({'error': error.msg}, 400)


class Node(HTTPServer):

    def __init__(self, port=8181):
        self.port = port
        self.chain = Blockchain()
        server_address = ('', port)
        super().__init__(server_address, NodeServerHandler)

    def serve(self):
        try:
            self.serve_forever()
        finally:
            self.server_close()

    @classmethod
    def run(cls, port=8181, handler_class=NodeServerHandler):
        return cls(port=port).serve()


if __name__ == '__main__':
    Node.run()
