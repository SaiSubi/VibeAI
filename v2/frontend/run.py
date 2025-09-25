#!/usr/bin/env python3
"""
VibeAI v2 Frontend Runner
Run this to start the VibeAI v2 web interface
"""

import os
import sys

# Add the parent directory to Python path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from app import app

if __name__ == '__main__':
    print("🎵 Starting VibeAI v2 Frontend...")
    print("🌐 Open your browser to: http://localhost:5001")
    print("📱 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5001)
