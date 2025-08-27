from fastapi import FastAPI, APIRouter
from typing import List, Dict, Any, Optional

def apply_security_requirements(app: FastAPI):
    """
    Apply security requirements to all endpoints in the application.
    
    This function adds security requirements to all endpoints based on their tags.
    Different security schemes are applied to different endpoint groups.
    """
    # Define security requirements by tag
    tag_security_map = {
        "auth": ["bearerAuth"],  # Auth endpoints use JWT only
        "products": ["bearerAuth", "apiKeyAuth"],  # Products can use both JWT and API key
        "orders": ["bearerAuth"],  # Orders require JWT auth
        "users": ["bearerAuth"],  # User management requires JWT auth
        "analytics": ["bearerAuth", "apiKeyAuth"],  # Analytics can use both
    }
    
    # Apply security requirements to routes based on tags
    for route in app.routes:
        if not hasattr(route, "tags") or not route.tags:
            continue
            
        # Skip authentication endpoints that don't require auth
        if "auth" in route.tags and getattr(route, "path", "").endswith(("/signup", "/token")):
            continue
            
        # Get security requirements for this route's tags
        security_requirements = []
        for tag in route.tags:
            if tag.lower() in tag_security_map:
                for scheme in tag_security_map[tag.lower()]:
                    security_requirement = {scheme: []}
                    if security_requirement not in security_requirements:
                        security_requirements.append(security_requirement)
        
        # Apply security requirements
        if security_requirements:
            if not hasattr(route, "security") or route.security is None:
                route.security = []
            for req in security_requirements:
                if req not in route.security:
                    route.security.append(req)

def add_security_examples(app: FastAPI):
    """
    Add security-related examples to the OpenAPI documentation.
    
    This function adds examples of security errors to the OpenAPI documentation.
    """
    # Define common security error responses
    security_responses = {
        "401": {
            "description": "Unauthorized",
            "content": {
                "application/json": {
                    "examples": {
                        "missing_token": {
                            "summary": "Missing authentication token",
                            "value": {"detail": "Not authenticated"}
                        },
                        "invalid_token": {
                            "summary": "Invalid authentication token",
                            "value": {"detail": "Could not validate credentials"}
                        },
                        "expired_token": {
                            "summary": "Expired authentication token",
                            "value": {"detail": "Token has expired"}
                        }
                    }
                }
            }
        },
        "403": {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "examples": {
                        "insufficient_permissions": {
                            "summary": "Insufficient permissions",
                            "value": {"detail": "Not enough permissions"}
                        },
                        "invalid_api_key": {
                            "summary": "Invalid API key",
                            "value": {"detail": "Invalid API key"}
                        }
                    }
                }
            }
        }
    }
    
    # Apply security responses to all secured routes
    for route in app.routes:
        if not hasattr(route, "security") or not route.security:
            continue
            
        if not hasattr(route, "responses") or not route.responses:
            route.responses = {}
            
        # Add security responses
        for status_code, response in security_responses.items():
            if status_code not in route.responses:
                route.responses[status_code] = response