#!/usr/bin/env python3
# Alibaba Cloud FC Custom Runtime HTTP server entrypoint
# Listens on port 9000 and delegates invocation to serverless.handler(event, context)

import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

# Import user code
import serverless as user_module

class FCHTTPHandler(BaseHTTPRequestHandler):
    def _send(self, status=200, body=b"", content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        # Health probe or unexpected path
        if self.path == "/healthz":
            self._send(200, b"OK", content_type="text/plain")
        else:
            self._send(404, b"Not Found", content_type="text/plain")

    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length', '0'))
            raw = self.rfile.read(length) if length > 0 else b"{}"
            sys.stdout.write(f"[index] Received POST {self.path}, length={length}\n")
            sys.stdout.flush()
            # FC sends JSON event; default to empty dict
            try:
                event = json.loads(raw.decode('utf-8') or '{}')
            except Exception:
                # If not JSON, pass as string
                event = {"body": raw.decode('utf-8', errors='ignore')}

            # Minimal context placeholder
            context = None

            # Delegate to user handler
            sys.stdout.write("[index] Calling user handler...\n")
            sys.stdout.flush()
            result = user_module.handler(event, context)

            # Normalize response
            if isinstance(result, (dict, list)):
                resp_body = json.dumps(result).encode('utf-8')
                self._send(200, resp_body)
            elif isinstance(result, (str, bytes)):
                body = result if isinstance(result, bytes) else result.encode('utf-8')
                self._send(200, body, content_type="text/plain")
            else:
                resp_body = json.dumps({"ok": True, "result": result}).encode('utf-8')
                self._send(200, resp_body)
        except Exception as e:
            err = {"ok": False, "error": str(e)}
            sys.stdout.write(f"[index] Error: {e}\n")
            sys.stdout.flush()
            self._send(500, json.dumps(err).encode('utf-8'))


def main():
    host = "0.0.0.0"
    port = 9000
    httpd = HTTPServer((host, port), FCHTTPHandler)
    sys.stdout.write(f"FC Custom Runtime HTTP server listening on {host}:{port}\n")
    sys.stdout.flush()
    httpd.serve_forever()

if __name__ == "__main__":
    main()
