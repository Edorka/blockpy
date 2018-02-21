from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse
import json
from http.client import HTTPConnection
from urllib.parse import urlencode


class APIClient():

    def connect(self, host):
        self.connection = HTTPConnection(host)

    def post(self, url='/', data={}):
        headers = {'Content-type': 'application/json'}
        json_str = json.dumps(data)
        self.connection.request('POST', url, json_str, headers)
        response = self.connection.getresponse()
        result = json.loads(response.read().decode('utf-8'))
        return response.status, result

    def get(self, url='/', params=None):
        headers = {'Content-type': 'application/json'}
        if params is not None:
            url += '?' + urlencode(params)
        self.connection.request('GET', url, headers=headers)
        response = self.connection.getresponse()
        result = json.loads(response.read().decode('utf-8'))
        return response.status, result

def when_get(url):
    def wrapper(fn):
        return APIHandler.when_get(url, fn)
    return wrapper


def when_post(url):
    def wrapper(fn):
        return APIHandler.when_post(url, fn)
    return wrapper


class UnknownMethod(Exception):
    pass


class APIHandler(BaseHTTPRequestHandler):
    methods_for_get = {}
    methods_for_post = {}

    @classmethod
    def when_post(cls, url, fn):
        cls.methods_for_post[url] = fn
        return fn

    @classmethod
    def when_get(cls, url, fn):
        cls.methods_for_get[url] = fn
        return fn

    def find_method(self, method, url):
        source = self.methods_for_post if method == 'post' else self.methods_for_get
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

    def do_GET(self):
        try:
            parsed = urlparse(self.path)
            method = self.find_method('get', parsed.path)
            code, result = method(self, params=parsed.params)
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
