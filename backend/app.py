from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys
import json
import mimetypes
import os
import socket

# Add project root to sys.path for imports when running as a script
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.optimizer.engine import optimize_code


ROOT = Path(__file__).parent.resolve()
PUBLIC = ROOT.parent / "frontend"


class OptimizerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/":
            path = "/index.html"

        file_path = (PUBLIC / path.lstrip("/")).resolve()
        if not is_public_file(file_path):
            self.send_error(404, "File not found")
            return

        self.send_static_file(file_path)

    def do_HEAD(self):
        path = self.path.split("?", 1)[0]
        if path == "/":
            path = "/index.html"

        file_path = (PUBLIC / path.lstrip("/")).resolve()
        if not is_public_file(file_path):
            self.send_error(404, "File not found")
            return

        self.send_static_headers(file_path)

    def send_static_file(self, file_path: Path):
        body = file_path.read_bytes()
        self.send_static_headers(file_path, content_length=len(body))
        self.wfile.write(body)

    def send_static_headers(self, file_path: Path, content_length: int | None = None):
        content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        if content_length is None:
            content_length = file_path.stat().st_size
        self.send_header("Content-Length", str(content_length))
        self.send_header("Cache-Control", "no-store, max-age=0")
        self.end_headers()

    def do_POST(self):
        if self.path != "/optimize":
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store, max-age=0")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Route not found"}).encode("utf-8"))
            return

        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length)

        try:
            payload = json.loads(raw_body.decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("Request body must be a JSON object.")

            source = payload.get("source", "")
            if not isinstance(source, str):
                raise ValueError("The 'source' field must be a string.")

            enabled_passes = payload.get("enabled_passes")
            if enabled_passes is not None and not isinstance(enabled_passes, list):
                raise ValueError("The 'enabled_passes' field must be a list when provided.")

            result = optimize_code(source, enabled_passes=enabled_passes)
        except Exception as exc:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store, max-age=0")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(exc)}).encode("utf-8"))
            return

        body = json.dumps(result, indent=2).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store, max-age=0")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print("[server]", fmt % args)


def main():
    requested_port = get_requested_port()
    server, port = create_server(requested_port)
    if port != requested_port:
        print(f"Port {requested_port} is already in use; using port {port} instead.", flush=True)

    print(f"AI-Assisted Code Optimization Compiler running at http://localhost:{port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.", flush=True)
    finally:
        server.server_close()


def get_requested_port() -> int:
    if len(sys.argv) > 1:
        return int(sys.argv[1])
    return int(os.environ.get("PORT", "8000"))


def find_available_port(start_port: int) -> int:
    port = start_port
    while not is_port_available(port):
        port += 1
    return port


def create_server(start_port: int) -> tuple[ThreadingHTTPServer, int]:
    port = start_port
    while port <= 65535:
        try:
            return ThreadingHTTPServer(("0.0.0.0", port), OptimizerHandler), port
        except OSError:
            port += 1

    raise OSError(f"No available port found at or above {start_port}.")


def is_port_available(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        return sock.connect_ex(("localhost", port)) != 0


def is_public_file(file_path: Path) -> bool:
    try:
        file_path.relative_to(PUBLIC)
    except ValueError:
        return False
    return file_path.is_file()


if __name__ == "__main__":
    main()
