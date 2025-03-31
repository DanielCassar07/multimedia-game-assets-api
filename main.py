from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from routes import router
from config import client
from security import RateLimiter
import re

app = FastAPI(
    title="Multimedia Game Assets API",
    description="A RESTful API for managing game assets including sprites, audio files, and player scores",
    version="1.0.0"
)

# Initialize rate limiter
rate_limiter = RateLimiter(requests_per_minute=100)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware for rate limiting and input sanitization
@app.middleware("http")
async def security_middleware(request: Request, call_next):
    # Get client IP
    client_ip = request.client.host
    
    # Check rate limit
    if not await rate_limiter.check_rate_limit(client_ip):
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded. Please try again later."}
        )
    
    # Check for potential NoSQL injection patterns in the URL
    url_path = str(request.url)
    
    # Simple pattern matching for NoSQL injection attempts
    suspicious_patterns = [
        r'\$where',
        r'\$ne',
        r'\$gt',
        r'\$lt',
        r'\$regex',
        r'\$exists',
        r'\.\.\/',
        r'\/\.\.',
        r'\$where',
        r'\$ne',
        r'\$gt',
        r'\$lt',
        r'\$regex',
        r'\$exists',
        r'\.\.\/',
        r'\/\.\.', 
        r';'
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, url_path, re.IGNORECASE):
            return JSONResponse(
                status_code=400,
                content={"detail": "Potential security threat detected in request"}
            )
    
    # Continue with the normal request processing
    response = await call_next(request)
    return response

# Include all routes
app.include_router(router)

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to the Multimedia Game Assets API",
        "docs_url": "/docs",
        "endpoints": {
            "sprites": "/sprites",
            "audio": "/audio",
            "scores": "/scores"
        }
    }

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    try:
        # Check if MongoDB is connected
        await client.admin.command('ping')
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)