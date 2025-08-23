#!/usr/bin/env python3
from __future__ import annotations
import os
import sys

TEMPLATE_INIT = """from fastapi import APIRouter, FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.plugins.base import PluginBase, PluginConfig

router = APIRouter()

@router.get("/")
async def list_items():
    return {{"{slug}s": []}}

class {ClassPrefix}Config(PluginConfig):
    enabled: bool = True

class Plugin(PluginBase):
    name = "{Title}"
    slug = "{slug}"
    version = "0.1.0"
    description = "{Title} plugin"
    author = "b2b-team"

    ConfigModel = {ClassPrefix}Config

    def register_routes(self, app: FastAPI) -> None:
        super().register_routes(app)
        app.include_router(router, prefix=f"/{self.slug}", tags=[self.name])

    async def init_db(self, engine: AsyncEngine) -> None:
        return None
"""

TEMPLATE_ROUTES = """from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health():
    return {{"ok": True, "plugin": "{slug}"}}
"""


def kebab_to_camel(s: str) -> str:
    return "".join(part.capitalize() for part in s.replace("_", "-").split("-"))


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: plugin_maker.py <slug> [Title]")
        return 2
    slug = argv[1]
    title = argv[2] if len(argv) >= 3 else slug.replace('-', ' ').title()
    class_prefix = kebab_to_camel(slug)

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    plugins_dir = os.path.join(repo_root, "plugins")
    os.makedirs(plugins_dir, exist_ok=True)

    plugin_dir = os.path.join(plugins_dir, slug)
    os.makedirs(plugin_dir, exist_ok=True)

    with open(os.path.join(plugin_dir, "__init__.py"), "w", encoding="utf-8") as f:
        f.write(TEMPLATE_INIT.format(slug=slug, Title=title, ClassPrefix=class_prefix))

    with open(os.path.join(plugin_dir, "routes.py"), "w", encoding="utf-8") as f:
        f.write(TEMPLATE_ROUTES.format(slug=slug))

    print(f"✅ Created plugin scaffold: {plugin_dir}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))