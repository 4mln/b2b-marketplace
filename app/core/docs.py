from fastapi.openapi.models import SecuritySchemeIn, SecurityScheme
from fastapi import FastAPI

def setup_api_documentation(app: FastAPI):
    """
    Configure OpenAPI documentation with security schemes and additional information.
    """
    
    # Update OpenAPI metadata
    app.openapi_tags = [
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
    ]
    
    # Add security schemes
    app.openapi_components = {
        "securitySchemes": {
            "bearerAuth": SecurityScheme(
                type="http",
                scheme="bearer",
                bearerFormat="JWT",
                description="JWT authentication token",
            ),
            "apiKeyAuth": SecurityScheme(
                type="apiKey",
                in_=SecuritySchemeIn.header,
                name="X-API-Key",
                description="API key for B2B integrations",
            ),
        }
    }
    
    # Global security requirements
    app.openapi_security = [
        {"bearerAuth": []},
        {"apiKeyAuth": []},
    ]
    
    # Additional OpenAPI metadata
    app.openapi_version = "3.0.2"
    app.openapi_info = {
        "title": app.title,
        "version": app.version,
        "description": """
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
        "contact": {
            "name": "API Support",
            "email": "api-support@example.com",
            "url": "https://example.com/support",
        },
        "license": {
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT",
        },
        "termsOfService": "https://example.com/terms",
    }