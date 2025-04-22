"""
Simple HTTP server that responds to health checks while the bot runs independently.
This file is used for production deployment on platforms like Koyeb.
"""
import os
import http.server
import socketserver
import threading
import logging
import time
from run_miku_bot_standalone import force_standalone_bot

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define handler for health checks
class HealthCheckHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health' or self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "ok", "bot": "running"}')
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def log_message(self, format, *args):
        logger.info("%s - - [%s] %s" % (self.client_address[0], self.log_date_time_string(), format % args))


def start_health_server():
    """Start a simple HTTP server to respond to health checks"""
    port = int(os.environ.get("PORT", 8000))
    handler = HealthCheckHandler
    
    with socketserver.TCPServer(("", port), handler) as httpd:
        logger.info(f"Health check server started at port {port}")
        httpd.serve_forever()


if __name__ == "__main__":
    # Start the bot in a separate thread
    bot_thread = threading.Thread(target=force_standalone_bot, daemon=True)
    bot_thread.start()
    
    # Start the health check server in the main thread
    try:
        start_health_server()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")