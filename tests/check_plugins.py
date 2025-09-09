# check_plugins.py
import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.main import app

def check_plugins():
    print("\n🌟 App State:")
    for key in dir(app.state):
        if not key.startswith('_'):
            print(f"- {key}")
    
    print("\n🌟 Loaded Plugins:")
    plugins = getattr(app.state, 'plugins', [])
    if plugins:
        for plugin in plugins:
            print(f"- {plugin.slug} (v{plugin.version})")
    else:
        print("No plugins loaded")
    
    print("\n🌟 Plugin Registry:")
    registry = getattr(app.state, 'plugin_registry', None)
    if registry:
        print(f"Routes registered: {len(registry.routes())}")
        for path, owner in registry.routes().items():
            print(f"- {path} -> {owner}")
    else:
        print("No plugin registry found")

if __name__ == "__main__":
    check_plugins()