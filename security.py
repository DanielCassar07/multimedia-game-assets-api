from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from dotenv import load_dotenv
from typing import Optional
import time
import re

load_dotenv()

# Simple API key validation
API_KEY = os.getenv("API_KEY", "test_api_key")

class APIKeyHeader(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(APIKeyHeader, self).__init__(auto_error=auto_error)
        
    async def __call__(self, request: Request) -> Optional[HTTPAuthorizationCredentials]:
        credentials: HTTPAuthorizationCredentials = await super(APIKeyHeader, self).__call__(request)
        
        if credentials:
            if credentials.scheme != "Bearer":
                raise HTTPException(
                    status_code=403, detail="Invalid authentication scheme."
                )
            if credentials.credentials != API_KEY:
                raise HTTPException(
                    status_code=403, detail="Invalid or expired API key."
                )
            return credentials.credentials
        else:
            raise HTTPException(
                status_code=403, detail="Invalid authorization credentials."
            )

# Rate limiting implementation
class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.request_history = {}
        
    async def check_rate_limit(self, ip_address: str) -> bool:
        current_time = time.time()
        
        # Remove requests older than 1 minute
        if ip_address in self.request_history:
            self.request_history[ip_address] = [
                timestamp for timestamp in self.request_history[ip_address]
                if current_time - timestamp < 60
            ]
        else:
            self.request_history[ip_address] = []
            
        # Check if rate limit is exceeded
        if len(self.request_history[ip_address]) >= self.requests_per_minute:
            return False
            
        # Add current request timestamp
        self.request_history[ip_address].append(current_time)
        return True
            
# Input sanitization for MongoDB
def sanitize_mongo_query(query_dict: dict) -> dict:
    """Sanitize MongoDB query to prevent NoSQL injection"""
    if not isinstance(query_dict, dict):
        return query_dict
        
    sanitized_query = {}
    
    for key, value in query_dict.items():
        # Check for MongoDB operator keys
        if key.startswith('$'):
            continue
            
        # Recursive sanitization for nested dictionaries
        if isinstance(value, dict):
            sanitized_query[key] = sanitize_mongo_query(value)
        elif isinstance(value, list):
            sanitized_query[key] = [
                sanitize_mongo_query(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            # Check for string values that might contain injection attempts
            if isinstance(value, str):
                if re.search(r'\$where|\$ne|\$gt|\$lt|\$regex|\$exists|\.\.\/|\/\.\.', value):
                    continue
            sanitized_query[key] = value
            
    return sanitized_query