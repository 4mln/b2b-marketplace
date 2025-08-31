from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.core.config import settings  # Assuming this is needed for APP_NAME, etc.; add if missing

def setup_api_documentation(app: FastAPI):
    """
    Configure OpenAPI documentation with security schemes and additional information.
    """
    
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        
        openapi_schema = get_openapi(
            title=settings.APP_NAME if hasattr(settings, 'APP_NAME') else "B2B Marketplace API",
            version=settings.APP_VERSION if hasattr(settings, 'APP_VERSION') else "0.1.0",
            description="""
            # B2B Marketplace API

            ## Authentication
            The API supports two authentication methods:
            * JWT Bearer token for user authentication
            * API Key for B2B integrations

            ## Rate Limiting
            API requests are limited to prevent abuse. Current limits:
            * 100 requests per minute per IP address
            * Exceeded limits will return 429 Too Many Requests

            ## Security
            * All endpoints require authentication
            * HTTPS is required for all API calls
            * JWT tokens expire after 30 minutes
            * Refresh tokens are valid for 7 days
            
            ## Error Handling
            The API uses standard HTTP status codes:
            * 2xx: Success
            * 4xx: Client errors
            * 5xx: Server errors
            
            Detailed error messages are provided in the response body.
            """,
            routes=app.routes,
            tags=[
                {
                    "name": "auth",
                    "description": "Authentication and authorization operations",
                },
                {
                    "name": "products",
                    "description": "Product management and catalog operations",
                },
                {
                    "name": "orders",
                    "description": "Order processing and management",
                },
                {
                    "name": "users",
                    "description": "User management operations",
                },
                {
                    "name": "analytics",
                    "description": "Business analytics and reporting",
                },
            ],
            contact={
                "name": "API Support",
                "email": "api-support@example.com",
                "url": "https://example.com/support",
            },
            license_info={
                "name": "MIT",
                "url": "https://opensource.org/licenses/MIT",
            },
            terms_of_service="https://example.com/terms",
        )
        
        # Add security schemes as dictionaries
        openapi_schema["components"]["securitySchemes"] = {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "JWT authentication token",
            },
            "apiKeyAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key",
                "description": "API key for B2B integrations",
            },
        }
        
        # Global security requirements
        openapi_schema["security"] = [
            {"bearerAuth": []},
            {"apiKeyAuth": []},
        ]
        
        # Additional OpenAPI metadata
        openapi_schema["openapi"] = "3.0.2"  # Set version directly
        
        app.openapi_schema = openapi_schema
        return app.openapi_schema
    
    app.openapi = custom_openapi