# app/main.py
# Fix Python path to include /code directory
import sys
if '/code' not in sys.path:
    sys.path.insert(0, '/code')

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine
from redis.asyncio import Redis
from app.core.config import settings
from app.core.plugins.loader import PluginLoader
from app.core.middleware import setup_middleware
from app.core.security import setup_security_middleware
from app.core.logging import setup_logging_middleware
from app.core.ip_security import setup_ip_security
from app.core.api_key import setup_api_key_management
from app.core.docs import setup_api_documentation
from app.core.security_docs import apply_security_requirements, add_security_examples
from fastapi.responses import JSONResponse
from fastapi import Request
from contextlib import asynccontextmanager

# Lifespan context manager for startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize services and load plugins
    try:
        loader = PluginLoader()
        await loader.load_all(app, engine)
        if settings.ENABLE_PLUGIN_HOT_RELOAD:
            loader.enable_hot_reload(app, engine)
            
        # Apply security documentation after plugins are loaded
        apply_security_requirements(app)
        add_security_examples(app)
    except Exception as e:
        print(f"Error loading plugins: {e}")
        raise
        
    yield  # This is where the app runs
    
    # Shutdown: cleanup connections
    await engine.dispose()
    await redis.close()

# Initialize FastAPI app with metadata
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="A secure and scalable B2B marketplace platform",
    docs_url="/api/docs",  # Swagger UI
    redoc_url="/api/redoc",  # ReDoc UI
    lifespan=lifespan
)
# Configure API documentation
setup_api_documentation(app)

# Setup API routes
import sys
print(f"Python path: {sys.path}")
try:
    from app.api.routes import setup_api_routes
    setup_api_routes(app)
except ImportError as e:
    print(f"Error importing routes: {e}")
    # Try alternative import path
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("routes", "/code/app/api/routes.py")
        routes_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(routes_module)
        routes_module.setup_api_routes(app)
        print("Successfully loaded routes from alternative path")
    except Exception as e2:
        print(f"Failed alternative import: {e2}")
        # Create router directly as fallback
        from fastapi import APIRouter
        api_router = APIRouter(prefix="/api/v1")
        app.include_router(api_router)
        print("Created fallback API router")


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else ["https://yourdomain.com"],  # Environment-aware
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import engine from session to avoid duplication
from app.db.session import async_engine as engine

# Create Redis connection
redis = Redis.from_url(
    settings.REDIS_URL,
    encoding="utf-8",
    decode_responses=True,
    max_connections=20
)

# Setup security middlewares
setup_security_middleware(app)
setup_logging_middleware(app)
setup_ip_security(app, redis)
setup_middleware(app, redis)  # Rate limiting

# Initialize API key manager
global api_key_manager
api_key_manager = setup_api_key_management(app, redis)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG
    }
# Engine and Redis variables are defined here for use in the lifespan context manager


@app.get("/manifest.json")
async def pwa_manifest():
    return JSONResponse(
        {
            "name": settings.APP_NAME,
            "short_name": settings.APP_NAME,
            "start_url": "/",
            "display": "standalone",
            "background_color": "#ffffff",
            "theme_color": "#0d9488",
            "icons": [],
            "lang": "fa",
            "dir": "rtl",
        }
    )


@app.get("/service-worker.js")
async def service_worker():
    js = (
        "self.addEventListener('install', e => { self.skipWaiting(); });\n"
        "self.addEventListener('activate', e => { self.clients.claim(); });\n"
        "self.addEventListener('fetch', e => { e.respondWith(fetch(e.request).catch(() => new Response('', {status: 200}))); });\n"
    )
    return JSONResponse(js, media_type="application/javascript")