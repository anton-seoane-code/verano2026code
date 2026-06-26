import json
import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.reader import scan_directory, read_file
from core.summarizer import generate_summary
from core.mindmap_gen import generate_mindmap
from core.quiz_gen import generate_quiz, format_quiz_markdown

PORT = int(os.environ.get("PORT", 8000))
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(SCRIPT_DIR, "static")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")


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
        files = scan_directory(directory)
        self._json_response({"files": files, "dir": directory})

    def _handle_generate(self, data):
        directory = data.get("dir", "")
        filenames = data.get("files", [])
        options = data.get("options", {})

        results = {}
        for fname in filenames:
            filepath = os.path.join(directory, fname)
            if not os.path.isfile(filepath):
                continue
            try:
                text = read_file(filepath)
            except Exception as e:
                results[fname] = {"error": str(e)}
                continue

            file_result = {}

            if options.get("summaries"):
                summary = generate_summary(text)
                outdir = os.path.join(OUTPUT_DIR, "summaries")
                os.makedirs(outdir, exist_ok=True)
                outpath = os.path.join(outdir, fname.rsplit(".", 1)[0] + "_summary.md")
                with open(outpath, "w") as f:
                    f.write(f"# Summary: {fname}\n\n{summary}\n")
                file_result["summary"] = {"path": outpath, "content": f"# Summary: {fname}\n\n{summary}\n"}

            if options.get("mindmaps"):
                mindmap = generate_mindmap(text, title=fname)
                outdir = os.path.join(OUTPUT_DIR, "mindmaps")
                os.makedirs(outdir, exist_ok=True)
                outpath = os.path.join(outdir, fname.rsplit(".", 1)[0] + "_mindmap.md")
                with open(outpath, "w") as f:
                    f.write(mindmap)
                file_result["mindmap"] = {"path": outpath, "content": mindmap}

            if options.get("quizzes"):
                questions = generate_quiz(text)
                quiz = format_quiz_markdown(questions, title=f"{fname} Quiz")
                outdir = os.path.join(OUTPUT_DIR, "quizzes")
                os.makedirs(outdir, exist_ok=True)
                outpath = os.path.join(outdir, fname.rsplit(".", 1)[0] + "_quiz.md")
                with open(outpath, "w") as f:
                    f.write(quiz)
                file_result["quiz"] = {
                    "path": outpath,
                    "content": quiz,
                    "questions": questions,
                }

            results[fname] = file_result

        self._json_response({"results": results})

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
