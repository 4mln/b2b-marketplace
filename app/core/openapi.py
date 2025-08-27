from typing import Dict, List, Any, Optional, Callable
from fastapi import FastAPI, APIRouter

def enhance_endpoint_docs(router: APIRouter, descriptions: Dict[str, Dict[str, Any]]):
    """
    Enhance API endpoint documentation with detailed descriptions, examples, and response schemas.
    
    Args:
        router: The APIRouter containing the endpoints to enhance
        descriptions: A dictionary mapping operation_ids to documentation details
    """
    for route in router.routes:
        if not hasattr(route, "operation_id") or not route.operation_id:
            continue
            
        operation_id = route.operation_id
        if operation_id not in descriptions:
            continue
            
        doc_details = descriptions[operation_id]
        
        # Update endpoint documentation
        if "summary" in doc_details:
            route.summary = doc_details["summary"]
            
        if "description" in doc_details:
            route.description = doc_details["description"]
            
        if "responses" in doc_details:
            if not hasattr(route, "responses") or not route.responses:
                route.responses = {}
            route.responses.update(doc_details["responses"])
            
        if "examples" in doc_details and hasattr(route, "examples"):
            route.examples = doc_details["examples"]

def add_security_requirement(router: APIRouter, security_scheme: str, scopes: Optional[List[str]] = None):
    """
    Add security requirement to all endpoints in a router.
    
    Args:
        router: The APIRouter to add security requirements to
        security_scheme: The name of the security scheme to apply
        scopes: Optional list of scopes required
    """
    for route in router.routes:
        if not hasattr(route, "security") or route.security is None:
            route.security = []
        
        requirement = {security_scheme: scopes or []}
        if requirement not in route.security:
            route.security.append(requirement)

def add_response_examples(router: APIRouter, operation_id: str, status_code: str, examples: Dict[str, Any]):
    """
    Add response examples to a specific endpoint.
    
    Args:
        router: The APIRouter containing the endpoint
        operation_id: The operation_id of the endpoint
        status_code: The HTTP status code for the examples
        examples: Dictionary of example responses
    """
    for route in router.routes:
        if not hasattr(route, "operation_id") or route.operation_id != operation_id:
            continue
            
        if not hasattr(route, "responses") or not route.responses:
            route.responses = {}
            
        if status_code not in route.responses:
            route.responses[status_code] = {}
            
        route.responses[status_code]["content"] = {
            "application/json": {
                "examples": examples
            }
        }