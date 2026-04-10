"""
Secret Guardian of Secrets — Local Launcher
============================================
Opens the Guardian web app in your default browser. No API key, no
install, no dependencies beyond Python's standard library.

    python secret_guardian.py

The app itself lives in index.html (same directory). This script just
serves it locally so file:// permission quirks don't apply, then opens
your browser to it. It also works standalone on GitHub Pages — this
launcher is purely a convenience for people who clone the repo.
"""

import http.server
import os
import socketserver
import sys
import threading
import webbrowser

PORT = 0  # let the OS pick a free port
DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    os.chdir(DIR)
    handler = http.server.SimpleHTTPRequestHandler

    with socketserver.TCPServer(("127.0.0.1", PORT), handler) as httpd:
        actual_port = httpd.server_address[1]
        url = f"http://127.0.0.1:{actual_port}/index.html"

        # Serve in a daemon thread so the script exits cleanly on Ctrl-C.
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()

        print(f"Serving Secret Guardian at {url}")
        print("Press Ctrl-C to stop.\n")
        webbrowser.open(url)

        try:
            thread.join()
        except KeyboardInterrupt:
            print("\n(the Guardian fades back into the reeds.)")
            httpd.shutdown()


if __name__ == "__main__":
    main()
