# app/main.py
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

# Initialize FastAPI app with metadata
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="A secure and scalable B2B marketplace platform",
    docs_url="/api/docs",  # Swagger UI
    redoc_url="/api/redoc"  # ReDoc UI
)

# Configure API documentation
setup_api_documentation(app)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create async database engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=10
)

# Create Redis connection
redis = Redis.from_url(
    settings.REDIS_URL,
    encoding="utf-8",
    decode_responses=True,
    max_connections=20
)

# Initialize API key manager
api_key_manager = None

# Startup event: initialize services and load plugins
@app.on_event("startup")
async def startup_event():
    global api_key_manager
    
    # Setup security middlewares
    setup_security_middleware(app)
    setup_logging_middleware(app)
    setup_ip_security(app, redis)
    setup_middleware(app, redis)  # Rate limiting
    api_key_manager = setup_api_key_management(app, redis)
    
    # Load and initialize plugins
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

# Shutdown event: cleanup connections
@app.on_event("shutdown")
async def shutdown_event():
    await engine.dispose()
    await redis.close()