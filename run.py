#!/usr/bin/env python3
"""
CSV Email Tool - Web Interface Launcher
Run this file to start the web interface
"""

import sys
import os

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Now import and run the app
if __name__ == "__main__":
    import uvicorn
    from api.app import app

    print("\n" + "="*70)
    print("  CSV EMAIL TOOL - WEB INTERFACE")
    print("="*70)
    print("\n🚀 Starting web server...")
    print("\n📂 Project directory:", current_dir)
    print("\n🌐 Open your browser to: http://localhost:8000")
    print("\n⏹️  Press CTRL+C to stop the server")
    print("\n" + "="*70 + "\n")

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )
