"""Rate limiting middleware for API endpoints."""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple rate limiting middleware using in-memory storage.
    
    For production, consider using Redis or a dedicated rate limiting service.
    """
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)  # {ip: [timestamp1, timestamp2, ...]}
    
    async def dispatch(self, request: Request, call_next):
        """Process request and check rate limits."""
        
        # Skip rate limiting for health checks, webhooks, and CORS preflight requests
        if request.url.path in ["/", "/health", "/api/webhooks/sendgrid", "/api/webhooks/gmail"] or request.method == "OPTIONS":
            return await call_next(request)
        
        # Get client IP
        client_ip = request.client.host
        
        # Get current time
        now = datetime.utcnow()
        cutoff = now - timedelta(minutes=1)
        
        # Clean old requests
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if req_time > cutoff
        ]
        
        # Check rate limit
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded. Please try again later.",
                    "limit": self.requests_per_minute,
                    "window": "1 minute"
                }
            )
        
        # Add current request
        self.requests[client_ip].append(now)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(
            self.requests_per_minute - len(self.requests[client_ip])
        )
        
        return response
