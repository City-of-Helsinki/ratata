import threading
import requests

from http.server import BaseHTTPRequestHandler, HTTPServer

HOST = '127.0.0.1'
PORT = 10231


class HTTPTestServer(BaseHTTPRequestHandler):

    def __clean_a_bit(self, path):
        if path.endswith('/'):
            path = path[0:-1]
        path = path.split('?', 1)[0]
        return path

    def __execute_method(self, path, method_type='GET'):
        method_name = "{0}{1}".format(method_type, path.replace('/', '_'))
        try:
            method = getattr(self, method_name)
            content = method()
            self.wfile.write(bytes(content, "utf8"))
        except AttributeError:
            self.GET_not_found()

    def do_POST(self):
        print("HTTPTestServer >> received POST to %s" % self.path)
        path = self.__clean_a_bit(self.path)
        self.__execute_method(path, 'POST')

    def do_GET(self):
        print("HTTPTestServer >> received GET to %s" % self.path)
        path = self.__clean_a_bit(self.path)
        self.__execute_method(path)

    def GET_test(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        return 'all ok'

    def GET_not_found(self):
        self.send_response(404)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(bytes("not found", "utf8"))


class ServerThread(threading.Thread):

    def __init__(self, server_klass, *args, **kwargs):
        super(ServerThread, self).__init__(*args, **kwargs)
        self.server_klass = server_klass
        self.httpd = None

    def run(self):
        server_address = (HOST, PORT)
        print("start server on %s %s" % server_address)
        self.httpd = HTTPServer(server_address, self.server_klass)
        self.httpd.serve_forever()


def run(klass=HTTPTestServer):
    threaded_server = ServerThread(klass)
    threaded_server.start()
    return threaded_server


def stop(server_thread):
    server_thread.httpd.shutdown()
    server_thread.join()
    print('server thread was shut down')


# quick test
if __name__ == '__main__':
    t = run()
    ret = requests.get("http://{0}:{1}/test".format(HOST, PORT))
    assert ret.status_code == 200
    print(ret.text)
    stop(t)
