# top of file
from app.core.plugins.loader import PluginLoader, LoaderSettings
# REMOVE: from app.core.plugin_loader import load_plugins

# inside startup_event(), before printing routes:
try:
    loader_settings = LoaderSettings(plugins_package="plugins", enable_hot_reload=settings.ENABLE_PLUGIN_HOT_RELOAD)
    plugin_loader = PluginLoader(settings=loader_settings)
    app.state.plugin_config = settings.PLUGIN_CONFIG  # optional, used by PluginBase
    await plugin_loader.load_all(app, engine)
    # Keep a handle so you can introspect later if you want:
    app.state.plugin_registry = plugin_loader.registry
    print("🔌 Plugins loaded:", [p.slug for p in plugin_loader.registry.list()])
except Exception as e:
    print(f"❌ Error loading plugins: {e}")