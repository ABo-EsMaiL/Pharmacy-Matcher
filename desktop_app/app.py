"""
Pharmacy Matcher — Desktop Application Entry Point

Launches a pywebview window with the web-based UI.
All terminal output is suppressed — the user only sees the GUI.
"""

import sys
import os
from pathlib import Path

# Ensure project root is on the path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Fix encoding on Windows
if sys.platform == 'win32':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')


def main():
    try:
        import webview
    except ImportError:
        print("ERROR: pywebview is not installed.")
        print("Run: pip install pywebview")
        input("Press Enter to exit...")
        sys.exit(1)

    try:
        from backend import API
    except ImportError:
        from desktop_app.backend import API

    # Create API instance
    api = API()

    # Path to the HTML template
    html_path = Path(__file__).parent / "templates" / "index.html"
    if not html_path.exists():
        print(f"ERROR: Template not found: {html_path}")
        input("Press Enter to exit...")
        sys.exit(1)

    # Create the main window
    window = webview.create_window(
        title="Pharmacy Matcher — نظام مطابقة الأدوية",
        url=str(html_path.resolve()),
        js_api=api,
        width=1200,
        height=800,
        min_size=(900, 600),
        resizable=True,
        text_select=False,
    )

    # Give the API a reference to the window (for evaluate_js calls)
    api.set_window(window)

    # On window close, cleanup resources
    def on_closing():
        try:
            api.on_closing()
        except Exception:
            pass

    window.events.closing += on_closing

    # Start the application (blocks until window is closed)
    webview.start(
        debug=False,  # Set to True for development
        private_mode=False,  # Allow localStorage persistence
    )


if __name__ == "__main__":
    main()
