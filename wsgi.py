#!/usr/bin/env python3
"""
Production WSGI launcher from root directory.
Uses Waitress (cross-platform, production-grade WSGI server).
Run with:
    python wsgi.py
"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FLASK_APP_DIR = os.path.join(BASE_DIR, 'Flask Deployed App')
if FLASK_APP_DIR not in sys.path:
    sys.path.insert(0, FLASK_APP_DIR)

from app import app, get_port

if __name__ == '__main__':
    try:
        from waitress import serve
        port = get_port()
        print("=" * 60)
        print(" 🌿 PlantGuard AI - Production WSGI Server (Waitress)")
        print(f" 🚀 Serving on: http://127.0.0.1:{port}")
        print("=" * 60)
        serve(app, host='0.0.0.0', port=port, threads=6)
    except ImportError:
        port = get_port()
        print("Waitress not found, falling back to standard server...")
        app.run(host='0.0.0.0', port=port, debug=False)
