# fix_path.py
import sys
import os

# Add the code directory to the Python path
sys.path.insert(0, '/code')

# Print the updated path
print("Updated Python path:")
print(sys.path)

# Try importing app and plugins
try:
    import app
    print("Successfully imported app package")
except ImportError as e:
    print(f"Failed to import app package: {e}")

try:
    import plugins
    print("Successfully imported plugins package")
except ImportError as e:
    print(f"Failed to import plugins package: {e}")