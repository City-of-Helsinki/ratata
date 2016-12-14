import threading
import requests

from http.server import BaseHTTPRequestHandler, HTTPServer

HOST = '127.0.0.1'
PORT = 10232


class HTTPTestServer(BaseHTTPRequestHandler):

    def do_GET(self):
        print("TestServer >> request to %s" % self.path)
        path = self.path
        if path.endswith('/'):
            path = path[0:-2]
        method_name = "GET{0}".format(path.replace('/', '_'))
        content = getattr(self, method_name)()
        self.wfile.write(bytes(content, "utf8"))

    def GET_test(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        return 'all ok'


class TestServerThread(threading.Thread):

    def __init__(self, server_klass, *args, **kwargs):
        super(TestServerThread, self).__init__(*args, **kwargs)
        self.server_klass = server_klass
        self.httpd = None

    def run(self):
        print("run being called")
        server_address = (HOST, PORT)
        self.httpd = HTTPServer(server_address, self.server_klass)
        self.httpd.serve_forever()


def run(klass=HTTPTestServer):
    threaded_server = TestServerThread(klass)
    threaded_server.start()
    return threaded_server


def quit(server_thread):
    server_thread.httpd.shutdown()
    server_thread.join()
    print('server thread was shut down')


# quick test
if __name__ == '__main__':
    t = run()
    ret = requests.get("http://{0}:{1}/test".format(HOST, PORT))
    assert ret.status_code == 200
    print(ret.text)
    quit(t)
