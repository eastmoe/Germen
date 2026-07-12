"""Local end-to-end smoke test for HTTP MJPEG capture."""

from __future__ import annotations

import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import cv2

from germen.frame_sources import capture_input_source


JPEG = cv2.imencode(".jpg", cv2.imread(str(Path(__file__).parents[1] / "static" / "sample.png")))[1].tobytes()


class MjpegHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=frame")
        self.end_headers()
        try:
            for _ in range(10):
                self.wfile.write(b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + JPEG + b"\r\n")
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass

    def log_message(self, _format: str, *_args: object) -> None:
        pass


def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 0), MjpegHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with tempfile.TemporaryDirectory() as directory:
            url = f"http://127.0.0.1:{server.server_port}/cam.mjpg"
            output = capture_input_source(Path(directory), url, warmup_frames=2)
            image = cv2.imread(str(output))
            if image is None or image.size == 0:
                raise RuntimeError(f"Captured image is invalid: {output}")
            print(f"MJPEG capture passed: {url} -> {output} ({image.shape[1]}x{image.shape[0]})")
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
