#!/usr/bin/env python3
"""
Simple script to serve and open the API documentation locally.
"""
import os
import webbrowser
import http.server
import socketserver


def serve_docs(port: int = 8000) -> None:
    """Serve the docs directory over HTTP and open the docs in the default browser."""
    script_dir = os.path.dirname(__file__)
    docs_dir = os.path.join(script_dir, 'docs')
    if not os.path.isdir(docs_dir):
        print(f"Docs directory not found at {docs_dir}")
        return
    os.chdir(docs_dir)
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        url = f"http://localhost:{port}/index.html"
        print(f"Serving docs at {url}")
        webbrowser.open(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Docs server stopped")


if __name__ == '__main__':
    serve_docs()
