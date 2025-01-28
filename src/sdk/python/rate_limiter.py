"""Rate limiting implementation for the Vernachain SDK."""

import time
import asyncio
from dataclasses import dataclass
from typing import Dict, Optional
from .errors import RateLimitError

@dataclass
class TokenBucket:
    """Token bucket for rate limiting."""
    
    capacity: int
    refill_rate: float
    tokens: float = 0.0
    last_refill: float = 0.0

    def __post_init__(self):
        """Initialize with full bucket."""
        self.tokens = float(self.capacity)
        self.last_refill = time.time()

    async def consume(self, tokens: int = 1) -> None:
        """
        Consume tokens from the bucket.
        
        Args:
            tokens: Number of tokens to consume
            
        Raises:
            RateLimitError: If not enough tokens available
        """
        await self._refill()
        
        if self.tokens < tokens:
            # Calculate wait time
            required_tokens = tokens - self.tokens
            wait_time = required_tokens / self.refill_rate
            raise RateLimitError(
                f"Rate limit exceeded. Please wait {wait_time:.1f} seconds."
            )
            
        self.tokens -= tokens

    async def _refill(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_refill
        
        # Calculate new tokens
        new_tokens = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + new_tokens)
        self.last_refill = now


class RateLimiter:
    """Rate limiter using token bucket algorithm."""
    
    def __init__(self):
        # Default limits for different endpoints
        self.limits = {
            'default': TokenBucket(capacity=100, refill_rate=1.0),  # 100 requests per second
            'GET': TokenBucket(capacity=1000, refill_rate=10.0),    # 1000 requests per 100 seconds
            'POST': TokenBucket(capacity=50, refill_rate=0.5),      # 50 requests per 100 seconds
            '/transaction': TokenBucket(capacity=20, refill_rate=0.2)  # 20 transactions per 100 seconds
        }

    async def check_limit(self, method: str, endpoint: str) -> None:
        """
        Check rate limit for the given method and endpoint.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            
        Raises:
            RateLimitError: If rate limit exceeded
        """
        # Get the most restrictive bucket that applies
        bucket = self._get_bucket(method, endpoint)
        await bucket.consume()

    def _get_bucket(self, method: str, endpoint: str) -> TokenBucket:
        """Get the appropriate token bucket for the request."""
        # Check endpoint-specific bucket first
        for path, bucket in self.limits.items():
            if path != 'default' and path != method and path in endpoint:
                return bucket
                
        # Then check method-specific bucket
        if method in self.limits:
            return self.limits[method]
            
        # Fall back to default bucket
        return self.limits['default'] 