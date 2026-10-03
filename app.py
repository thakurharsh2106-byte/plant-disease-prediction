#!/usr/bin/env python3
"""
PlantGuard AI - Direct root launcher
"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FLASK_APP_DIR = os.path.join(BASE_DIR, 'Flask Deployed App')
if FLASK_APP_DIR not in sys.path:
    sys.path.insert(0, FLASK_APP_DIR)

from app import app, get_port

if __name__ == '__main__':
    port = get_port()
    print("=" * 60)
    print(" 🌿 PlantGuard AI - Plant Disease Prediction System")
    print(f" 🚀 Running on: http://127.0.0.1:{port}")
    print("=" * 60)
    app.run(host='0.0.0.0', port=port, debug=True)
