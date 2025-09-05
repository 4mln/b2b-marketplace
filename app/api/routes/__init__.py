from fastapi import APIRouter

# Define the main API router for the package-based routing setup
api_router = APIRouter(prefix="/api/v1")

def setup_api_routes(app):
    """Register core API routers. Plugins register themselves separately."""
    app.include_router(api_router)
