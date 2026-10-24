"""Read-only design preview. Not a replacement production server.

Serves frontend files and the existing Lab adapter only. Never imports main,
database or the scoring module, and rejects all writes. The prototype API is
deliberately unavailable so its truthful failure state can be reviewed.
"""
import argparse
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
import lab


class Preview(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT / 'frontend'), **kwargs)

    def json_response(self, value, status=200):
        content = json.dumps(value, allow_nan=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(content)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(content)

    def do_POST(self):
        self.json_response({'error': 'read_only_preview'}, 405)

    do_PUT = do_PATCH = do_DELETE = do_POST

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == '/api/health':
            return self.json_response({'scoring_path': 'unknown', 'design_preview': True})
        if path.startswith('/api/lab/'):
            if not lab.artifacts_available():
                return self.json_response({'error': 'artifacts_unavailable'}, 503)
            if path == '/api/lab/manifest':
                return self.json_response(lab.manifest())
            if path == '/api/lab/scenarios':
                return self.json_response({'scenarios': lab.scenarios()})
            if path == '/api/lab/underreporting':
                return self.json_response(lab.underreporting())
            if path.startswith('/api/lab/comparison/'):
                data = lab.comparison(path.rsplit('/', 1)[-1])
                return self.json_response(data or {'error': 'not_found'}, 200 if data else 404)
        if path.startswith('/api/'):
            return self.json_response({'error': 'prototype_api_disabled_in_design_preview'}, 503)
        if path in ('/lab', '/lab/'):
            self.path = '/lab.html'
        elif path in ('/apply', '/dashboard', '/pricing'):
            self.path = '/index.html'
        target = (ROOT / 'frontend' / urlsplit(self.path).path.lstrip('/')).resolve()
        if not target.is_relative_to(ROOT / 'frontend'):
            return self.send_error(404)
        if target.is_dir() and not (target / 'index.html').exists():
            return self.send_error(404)
        return super().do_GET()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    server = ThreadingHTTPServer(('127.0.0.1', args.port), Preview)
    print(f'Local read-only preview: http://127.0.0.1:{args.port}', flush=True)
    server.serve_forever()
