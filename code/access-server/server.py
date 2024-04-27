from http.server import BaseHTTPRequestHandler, HTTPServer

_PORT = 8421
_MASTER = [None, None]  # (host: str, port: str)

class _MyHTTPServer(BaseHTTPRequestHandler):
    def do_GET(self):
        global _MASTER
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            if _MASTER == [None, None]:
                _MASTER[0] = self.client_address[0]
                _MASTER[1] = self.headers["port"]
                self.send_header("Master", "True")
                self.end_headers()
                self.wfile.write(b"You are the master node.")
            else:
                self.send_header("Master_host", _MASTER[0])
                self.send_header("Master_port", _MASTER[1])
                self.send_header("Master", "False")
                self.end_headers()
                self.wfile.write(b"Please find the host and port of the master in the header.")
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"The access server is working properly.")
        elif self.path == "/leave":
            if _MASTER[0] == self.client_address[0]:
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                _MASTER = [None, None]
                self.wfile.write(b"Left.")
            else:
                self.send_response(403)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b"Forbidden.")
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"Outside of functionality.")

def run():
    print('Starting server...')

    # Server settings
    server_address = ('', _PORT)
    httpd = HTTPServer(server_address, _MyHTTPServer)
    print(f"Server is running on port {_PORT}.")
    httpd.serve_forever()

if __name__ == '__main__':
    run()