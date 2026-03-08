#!/usr/bin/env python3
"""Launch the Linta Niri Theme Designer in a browser.

Starts a local HTTP server (needed for JS module loading) and opens the designer.
"""

import http.server
import os
import sys
import threading
import webbrowser
from pathlib import Path

PORT = 8739
DESIGNER_DIR = Path(__file__).resolve().parent / "theme-designer"


def main() -> None:
    os.chdir(DESIGNER_DIR)

    handler = http.server.SimpleHTTPRequestHandler
    handler.log_message = lambda *a: None  # silence request logs

    server = http.server.HTTPServer(("127.0.0.1", PORT), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    url = f"http://127.0.0.1:{PORT}"
    print(f"Linta Theme Designer running at {url}")
    print("Press Ctrl+C to stop.")

    webbrowser.open(url)

    try:
        thread.join()
    except KeyboardInterrupt:
        print("\nStopped.")
        server.shutdown()


if __name__ == "__main__":
    main()
