from fastapi import FastAPI, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from .rate_limiter import limiter
from config import settings
from slowapi.middleware import SlowAPIMiddleware

def setup_middleware(app: FastAPI):

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )


    # Add rate limiting middleware
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)


    # Custom handler for rate limit exceeded

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_exceeded_handler(request, exc):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, details="Too many requests. Please try again later.")