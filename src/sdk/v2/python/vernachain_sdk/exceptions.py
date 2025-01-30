from typing import Optional

class VernachainError(Exception):
    """Base exception for all Vernachain SDK errors."""
    def __init__(self, message: str, details: Optional[dict] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

class HTTPError(VernachainError):
    """Raised when an HTTP request fails."""
    def __init__(self, status_code: int, message: str, details: Optional[dict] = None):
        self.status_code = status_code
        super().__init__(f"HTTP {status_code}: {message}", details)

class WebSocketError(VernachainError):
    """Raised when a WebSocket operation fails."""
    pass

class AuthenticationError(VernachainError):
    """Raised when authentication fails (e.g., invalid API key)."""
    pass

class ValidationError(VernachainError):
    """Raised when request validation fails."""
    pass

class NetworkError(VernachainError):
    """Raised when a network operation fails."""
    pass

class UnexpectedResponseError(VernachainError):
    """Raised when the server response doesn't match expected format."""
    pass

class WebSocketClosedError(VernachainError):
    """Raised when the WebSocket connection is closed unexpectedly."""
    pass

class TimeoutError(VernachainError):
    """Raised when an operation times out."""
    pass

class RateLimitError(VernachainError):
    """Raised when API rate limit is exceeded."""
    pass

class SerializationError(VernachainError):
    """Raised when data serialization/deserialization fails."""
    pass 