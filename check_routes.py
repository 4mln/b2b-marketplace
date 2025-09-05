# check_routes.py
import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from fastapi import FastAPI
from app.main import app

def print_routes():
    print("\n🌟 Registered routes:")
    for route in app.routes:
        if hasattr(route, "path"):
            print(f"{route.path} -> {route.name}")

if __name__ == "__main__":
    print_routes()