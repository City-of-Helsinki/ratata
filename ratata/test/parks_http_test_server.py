#!/usr/bin/env python3
import json
import requests
from .http_test_server import HTTPTestServer, run, quit

HOST = '127.0.0.1'
PORT = 10231


def respond_json(func):
    def rapper(obj):
        print("return json for", func)
        obj.send_header('Content-type', 'application/json')
        obj.end_headers()
        return json.dumps(func(obj))
    return rapper


def respond_with(status):
    def decorator(func):
        def raps(obj):
            print("respond with ", status)
            obj.send_response(status)
            return func(obj)
        return raps
    return decorator


class ParksHTTPTestServer(HTTPTestServer):

    @respond_with(200)
    @respond_json
    def GET_parks(self):
        return {'parks': [1, 2, 3]}

    @respond_with(200)
    @respond_json
    def GET_parks_1(self):
        return {'id': 1, 'name': 'Porkie Park', 'description': 'Very fancy'}

    @respond_with(404)
    @respond_json
    def GET_parks_100(self):
        return {'status': 'park %s not found' % '100'}




# quick test
if __name__ == '__main__':
    t = run(ParksHTTPTestServer)
    ret = requests.get("http://{0}:{1}/parks/1".format(HOST, PORT))
    assert ret.status_code == 200
    print(ret.text)
    quit(t)
