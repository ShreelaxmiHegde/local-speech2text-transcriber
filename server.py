import json
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from transcriber import AudioTranscriber

# Shared transcriber instance
transcriber = AudioTranscriber()

class TranscriberAPIHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler providing REST API endpoints with CORS support."""

    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(204)
        self._send_cors_headers()
        self.end_headers()

    def _send_json(self, status_code, payload):
        """Sends a JSON response with CORS headers."""
        response_bytes = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self._send_cors_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.end_headers()
        self.wfile.write(response_bytes)

    def do_GET(self):
        """Handle GET requests."""
        if self.path == "/api/status":
            self._send_json(200, transcriber.get_status())
        else:
            self._send_json(404, {"error": "Endpoint not found"})

    def do_POST(self):
        """Handle POST action endpoints."""
        if self.path == "/api/start":
            ok, msg = transcriber.start()
            status_code = 200 if ok else 400
            self._send_json(status_code, {
                "success": ok,
                "message": msg,
                "status": transcriber.state
            })

        elif self.path == "/api/pause":
            ok, msg = transcriber.pause()
            status_code = 200 if ok else 400
            self._send_json(status_code, {
                "success": ok,
                "message": msg,
                "status": transcriber.state
            })

        elif self.path == "/api/resume":
            ok, msg = transcriber.resume()
            status_code = 200 if ok else 400
            self._send_json(status_code, {
                "success": ok,
                "message": msg,
                "status": transcriber.state
            })

        elif self.path == "/api/stop":
            result = transcriber.stop_and_transcribe()
            status_code = 200 if result.get("success") else 500
            result["status"] = transcriber.state
            self._send_json(status_code, result)

        else:
            self._send_json(404, {"error": "Endpoint not found"})

    def log_message(self, format, *args):
        """Format request logs cleanly."""
        print(f"[API] {self.command} {self.path} - {args[1]}")


def run_server(host="127.0.0.1", port=5000):
    server_address = (host, port)
    httpd = ThreadingHTTPServer(server_address, TranscriberAPIHandler)
    print(f"\033[92mServer running at http://{host}:{port}/\033[0m")
    print("Endpoints available:")
    print("  GET  /api/status")
    print("  POST /api/start")
    print("  POST /api/pause")
    print("  POST /api/resume")
    print("  POST /api/stop")
    print("\nPress Ctrl+C to stop the server.\n")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\033[93mShutting down server...\033[0m")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    run_server()
