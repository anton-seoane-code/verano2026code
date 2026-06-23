#!/usr/bin/env python3
import json
import mimetypes
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse

from analyzer import scan, find_duplicates, organize, generate_report

STATIC_DIR = Path(__file__).parent / 'static'
PORT = 8080

MIME_MAP = {
    '.html': 'text/html; charset=utf-8',
    '.css': 'text/css; charset=utf-8',
    '.js': 'application/javascript; charset=utf-8',
    '.json': 'application/json',
    '.png': 'image/png',
    '.ico': 'image/x-icon',
    '.svg': 'image/svg+xml',
}


def paths_to_strs(obj):
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, dict):
        return {k: paths_to_strs(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [paths_to_strs(i) for i in obj]
    return obj


class AnalyzerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == '/':
            path = '/index.html'

        filepath = STATIC_DIR / path.lstrip('/')
        filepath = filepath.resolve()

        if not str(filepath).startswith(str(STATIC_DIR.resolve())) or not filepath.is_file():
            self.send_error(404, 'File not found')
            return

        mime = MIME_MAP.get(filepath.suffix.lower(), 'application/octet-stream')
        try:
            data = filepath.read_bytes()
            self.send_response(200)
            self.send_header('Content-Type', mime)
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except OSError:
            self.send_error(500, 'Error reading file')

    def do_POST(self):
        parsed = urlparse(self.path)

        content_length = int(self.headers.get('Content-Length', 0))
        raw = self.rfile.read(content_length) if content_length else b'{}'
        try:
            body = json.loads(raw)
        except json.JSONDecodeError:
            self.send_json({'success': False, 'error': 'Invalid JSON'}, 400)
            return

        if parsed.path == '/api/browse':
            self.handle_browse(body)
        elif parsed.path == '/api/analyze':
            self.handle_analyze(body)
        elif parsed.path == '/api/organize':
            self.handle_organize(body)
        else:
            self.send_json({'success': False, 'error': 'Not found'}, 404)

    def send_json(self, data, status=200):
        payload = json.dumps(paths_to_strs(data), indent=2).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def handle_browse(self, body):
        path = body.get('path', '/')
        try:
            p = Path(path).resolve()
            if not p.is_dir():
                self.send_json({'success': False, 'error': 'Not a directory'}, 400)
                return

            dirs = sorted([d for d in p.iterdir() if d.is_dir()])
            files = sorted([f for f in p.iterdir() if f.is_file()])
            parent = str(p.parent) if p.parent != p else None

            self.send_json({
                'success': True,
                'path': str(p),
                'directories': [str(d) for d in dirs],
                'files': [f.name for f in files],
                'parent': parent,
            })
        except PermissionError:
            self.send_json({'success': False, 'error': 'Permission denied'}, 403)
        except OSError as e:
            self.send_json({'success': False, 'error': str(e)}, 500)

    def handle_analyze(self, body):
        directory = body.get('directory', '')
        recursive = body.get('recursive', False)
        detect_duplicates = body.get('detect_duplicates', True)

        if not directory:
            self.send_json({'success': False, 'error': 'No directory specified'}, 400)
            return

        try:
            categories, unrecognized = scan(directory, recursive)
        except (NotADirectoryError, PermissionError, FileNotFoundError) as e:
            self.send_json({'success': False, 'error': str(e)}, 400)
            return

        all_files = []
        for v in categories.values():
            all_files.extend(v)
        all_files.extend(unrecognized)

        duplicates = find_duplicates(all_files) if detect_duplicates else None

        total_files = sum(len(v) for v in categories.values()) + len(unrecognized)
        report = generate_report(categories, unrecognized, duplicates, None, directory)

        self.send_json({
            'success': True,
            'directory': directory,
            'categories': {k: [str(f) for f in v] for k, v in categories.items()},
            'unrecognized': [str(f) for f in unrecognized],
            'duplicates': duplicates,
            'duplicate_count': sum(len(v) for v in (duplicates or {}).values()),
            'duplicate_groups': len(duplicates or {}),
            'total_files': total_files,
            'recursive': recursive,
            'report': report,
        })

    def handle_organize(self, body):
        directory = body.get('directory', '')
        recursive = body.get('recursive', False)
        copy = body.get('copy', False)

        if not directory:
            self.send_json({'success': False, 'error': 'No directory specified'}, 400)
            return

        try:
            categories, unrecognized = scan(directory, recursive)
        except (NotADirectoryError, PermissionError, FileNotFoundError) as e:
            self.send_json({'success': False, 'error': str(e)}, 400)
            return

        organize_stats = organize(categories, directory, copy)
        organize_stats['_copy'] = copy

        report = generate_report(categories, unrecognized, None, organize_stats, directory)

        self.send_json({
            'success': True,
            'directory': directory,
            'stats': organize_stats,
            'action': 'copy' if copy else 'move',
            'report': report,
        })

    def log_message(self, format, *args):
        print(f'[server] {args[0]} {args[1]} {args[2]}')


def main():
    server = HTTPServer(('0.0.0.0', PORT), AnalyzerHandler)
    print(f'Directory Analyzer server running at http://localhost:{PORT}')
    print('Press Ctrl+C to stop')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nShutting down...')
        server.server_close()


if __name__ == '__main__':
    main()
