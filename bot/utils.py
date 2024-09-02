from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# Health check server configuration
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"OK")

def run_health_check_server(port=8080):
    server_address = ('', port)
    httpd = HTTPServer(server_address, HealthCheckHandler)
    print(f'Starting health check server on port {port}')
    httpd.serve_forever()

# Function to start the health check server in a separate thread
def start_health_check_server():
    thread = threading.Thread(target=run_health_check_server)
    thread.daemon = True
    thread.start()