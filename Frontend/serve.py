import os
from http.server import SimpleHTTPRequestHandler, HTTPServer

class CustomHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/html/index.html'
        elif self.path == '/register':
            self.path = '/html/register.html'
        elif self.path == '/pong':
            self.path = '/html/pong.html'
        else:
            self.path = '/html/index.html'
        return super().do_GET()

if __name__ == '__main__':
    # Ensure the server works in the correct directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Serve on all addresses, port 8000
    server_address = ('', 8000)
    
    # Create and start the HTTP server
    httpd = HTTPServer(server_address, CustomHandler)
    print("Serving on port 8000")
    httpd.serve_forever()
