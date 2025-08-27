import logging
import json
from datetime import datetime
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        # Start timer
        start_time = datetime.utcnow()
        
        # Process request
        response = await call_next(request)
        
        # Calculate request duration
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        # Extract request details
        log_data = {
            'timestamp': start_time.isoformat(),
            'method': request.method,
            'path': request.url.path,
            'status_code': response.status_code,
            'duration': duration,
            'client_ip': request.client.host,
            'user_agent': request.headers.get('user-agent'),
            'referer': request.headers.get('referer'),
            'query_params': str(request.query_params),
            'request_id': response.headers.get('X-Request-ID'),
        }
        
        # Log request details
        logger.info(json.dumps(log_data))
        
        return response

def setup_logging_middleware(app: FastAPI):
    app.add_middleware(RequestLoggingMiddleware)