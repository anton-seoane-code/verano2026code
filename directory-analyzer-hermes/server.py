#!/usr/bin/env python3
"""
Directory Analyzer — Web GUI Server
Serves the web interface and provides JSON API endpoints.
"""
import json
import re
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

from analyzer import scan, find_duplicates, organize, generate_report, CATEGORY_DIRS

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
    """Recursively convert Path objects to strings for JSON serialization."""
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, dict):
        return {k: paths_to_strs(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [paths_to_strs(i) for i in obj]
    return obj


class AnalyzerHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the analyzer web interface."""

    def do_GET(self):
        path = self.path
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
        parsed = self.path

        content_length = int(self.headers.get('Content-Length', 0))
        raw = self.rfile.read(content_length) if content_length else b'{}'
        try:
            body = json.loads(raw)
        except json.JSONDecodeError:
            self.send_json({'success': False, 'error': 'Invalid JSON'}, 400)
            return

        routes = {
            '/api/browse': self.handle_browse,
            '/api/analyze': self.handle_analyze,
            '/api/organize': self.handle_organize,
        }

        handler = routes.get(parsed)
        if handler:
            handler(body)
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

            # Count files per category for quick stats
            total_files = len(files)

            parent = str(p.parent) if p.parent != p else None

            self.send_json({
                'success': True,
                'path': str(p),
                'name': p.name,
                'directories': [{'name': d.name, 'path': str(d)} for d in dirs],
                'files': [f.name for f in files],
                'file_count': total_files,
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
            'category_counts': {k: len(v) for k, v in categories.items()},
            'unrecognized': [str(f) for f in unrecognized],
            'unrecognized_count': len(unrecognized),
            'duplicates': duplicates,
            'duplicate_count': sum(len(v) for v in (duplicates or {}).values()),
            'duplicate_groups': len(duplicates or {}),
            'total_files': total_files,
            'recursive': recursive,
            'report': report,
            'category_dirs': CATEGORY_DIRS,
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

        created_dirs = []
        for cat, st in organize_stats.items():
            if cat.startswith('_'):
                continue
            if st['moved'] > 0:
                created_dirs.append(str(Path(directory) / CATEGORY_DIRS[cat]))

        self.send_json({
            'success': True,
            'directory': directory,
            'stats': organize_stats,
            'action': 'copy' if copy else 'move',
            'created_directories': created_dirs,
            'report': report,
        })

    def log_message(self, _format, *args):
        print(f'[server] {args[0]} {args[1]} {args[2]}')


def main():
    server = HTTPServer(('0.0.0.0', PORT), AnalyzerHandler)
    print(f'  Directory Analyzer — Web GUI')
    print(f'  ─────────────────────────────')
    print(f'  Open: http://localhost:{PORT}')
    print(f'  Press Ctrl+C to stop')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n  Shutting down...')
        server.server_close()


if __name__ == '__main__':
    main()
