import json
import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

PORT = int(os.environ.get("PORT", 8000))
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")


class StudyAssistantHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length else "{}"
        data = json.loads(body) if body else {}

        if self.path == "/api/scan":
            self._handle_scan(data)
        elif self.path == "/api/generate":
            self._handle_generate(data)
        else:
            self.send_error(404)

    def _handle_scan(self, data):
        directory = data.get("dir", "")
        if not os.path.isdir(directory):
            self._json_response({"error": "Directory not found"}, 400)
            return
        files = []
        for entry in sorted(os.listdir(directory)):
            if entry.endswith((".txt", ".pdf")):
                full = os.path.join(directory, entry)
                if os.path.isfile(full):
                    files.append({"name": entry, "size": os.path.getsize(full)})
        self._json_response({"files": files, "dir": directory})

    def _handle_generate(self, data):
        self._json_response({"error": "Not yet implemented"}, 501)

    def _json_response(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode("utf-8"))

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/"):
            self._json_response({"error": "Not found"}, 404)
            return
        if parsed.path == "/":
            self.path = "/index.html"
        return super().do_GET()


def main():
    os.chdir(STATIC_DIR)
    server = HTTPServer(("0.0.0.0", PORT), StudyAssistantHandler)
    print(f"Study Assistant server at http://localhost:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == "__main__":
    main()
