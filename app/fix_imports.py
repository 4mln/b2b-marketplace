# app/fix_imports.py
import sys
import os

# Add the code directory to the Python path
def fix_path():
    if '/code' not in sys.path:
        sys.path.insert(0, '/code')
        print("Added /code to Python path")
    return True