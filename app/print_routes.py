# app/print_routes.py
from fastapi import FastAPI
from app.core.plugins import load_plugins
from app.core.db import engine  # your AsyncEngine
import asyncio

async def main():
    from app.main import app  # your FastAPI app

    # Load plugins (register routes)
    plugins = await load_plugins(app, engine)

    print("\n🌟 Registered routes:")
    for route in app.routes:
        if hasattr(route, "path"):
            print(f"{route.path} -> {route.name}")

    print("\n🌟 Plugin prefixes:")
    for plugin in plugins:
        # ✅ Get prefix from instance
        prefix = getattr(plugin, "_prefix", None)
        if prefix:
            print(f"{plugin.__class__.__name__}: {prefix}")
        else:
            print(f"{plugin.__class__.__name__}: No prefix set")

# Run in async loop
if __name__ == "__main__":
    asyncio.run(main())