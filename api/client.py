from http.client import HTTPConnection
import json
from urllib.parse import urlencode


class APIClient():

    def __init__(self, host):
        self.host = host
        self.connect(host)

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
