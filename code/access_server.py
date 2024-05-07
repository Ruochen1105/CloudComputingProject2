"""
Ruochen Miao rm5327 and Chengying Wang cw4450
"""
from http.server import BaseHTTPRequestHandler, HTTPServer

_PORT = 8421
_MASTER = [None, None]  # (host: str, port: str)

class _MyHTTPServer(BaseHTTPRequestHandler):
    # answering HTTP GET
    def do_GET(self):

        global _MASTER

        if self.path == "/": # get the host and port of the master node
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            if _MASTER == [None, None]:    # when there is no master node
                _MASTER[0] = self.client_address[0]
                _MASTER[1] = self.headers["port"]
                self.send_header("Master", "True")
                self.end_headers()
                self.wfile.write(b"You are the master node.")
            else:   # when there is master node
                self.send_header("Master_host", _MASTER[0])
                self.send_header("Master_port", _MASTER[1])
                self.send_header("Master", "False")
                self.end_headers()
                self.wfile.write(b"Please find the host and port of the master in the header.")

        elif self.path == "/health": # healthcheck
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"The access server is working properly.")

        elif self.path == "/leave": # the master node can leave the network if there are no more peers
            if _MASTER[0] == self.client_address[0]:    # if is from the master
                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                _MASTER = [None, None]
                self.wfile.write(b"Left.")
                print("The master left without specifying a successor.")
            else:    # if is not from the master
                self.send_response(403)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(b"Forbidden.")

        # it should be HTTP POST, but for the simplicity I'm also using GET
        elif self.path == "/new": # the master node leave the network while specifying a successor
            if _MASTER[0] == self.client_address[0]:    # if is from the master
                self.send_response(200)
                self.send_header("Contnent-type", "text/plain")
                _MASTER[0] = self.headers["host"]
                _MASTER[1] = self.headers["port"]
                self.end_headers()
                self.wfile.write(b"New master recorded.")
            else:    # if is not from the master
                self.send_response(403)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(b"Forbidden.")

        else:
            self.send_response(404)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Outside of functionality.")

def run():
    print("Starting server...")

    # Server settings
    server_address = ('', _PORT)
    httpd = HTTPServer(server_address, _MyHTTPServer)
    print(f"Server is running on port {_PORT}.")
    httpd.serve_forever()

if __name__ == '__main__':
    run()