from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
from http.server import HTTPServer
import socket
from time import sleep


class UnknownMethod(Exception):
    pass


class APIServer(HTTPServer):
    allow_reuse_address = True

    def __init__(self, app, port=8181):
        self.app = app
        self.listen(port)

    def listen(self, port, retry=6):
        while retry:
            try:
                server_address = ('', port)
                super().__init__(server_address, self.app.serve)
                break
            except socket.error as error:
                retry -= 1
                if retry is 0:
                    raise error
                sleep(0.25)

    def serve(self):
        try:
            self.serve_forever()
        finally:
            self.server_close()


class APIHandler(BaseHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        self.post_routes = {}
        self.get_routes = {}
        self.put_routes = {}

    def serve(self, *args, **kwargs):
        """
        Will provide a parent class instance for every incomin connection
        """
        super().__init__(*args, **kwargs)

    def when_post(self, url):
        def decorator(f):
            self.post_routes[url] = f
            return f
        return decorator

    def when_get(self, url):
        def decorator(f):
            self.get_routes[url] = f
            return f
        return decorator

    def when_put(self, url):
        def decorator(f):
            self.put_routes[url] = f
            return f
        return decorator

    def find_method(self, method, url):
        source = {}
        if method == 'post':
            source = self.post_routes
        elif method == 'get':
            source = self.get_routes
        elif method == 'put':
            source = self.put_routes
        for method_url, method in source.items():
            if url == method_url:
                return method
        else:
            raise UnknownMethod

    def reply(self, code, result):
        self.send_response(code)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        json_string = json.dumps(result)
        self.wfile.write(json_string.encode('utf-8'))

    def do_POST(self):
        try:
            parsed = urlparse(self.path)
            method = self.find_method('post', parsed.path)
            data = self.extract_json()
            code, result = method(self, data)
        except UnknownMethod:
            code, result = 404, {'error': 'method not found'}
        self.reply(code, result)

    def do_PUT(self):
        try:
            parsed = urlparse(self.path)
            method = self.find_method('put', parsed.path)
            data = self.extract_json()
            code, result = method(self, data)
        except UnknownMethod:
            code, result = 404, {'error': 'method not found'}
        self.reply(code, result)

    def do_GET(self):
        try:
            parsed = urlparse(self.path)
            method = self.find_method('get', parsed.path)
            params = parse_qs(parsed.query)
            code, result = method(self, params=params)
        except UnknownMethod:
            code, result = 404, {'error': 'method not found'}
        self.reply(code, result)

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
