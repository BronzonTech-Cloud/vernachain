"""Custom exceptions for the Vernachain SDK."""

class VernachainError(Exception):
    """Base exception for all Vernachain SDK errors."""
    pass

class TransactionError(VernachainError):
    """Raised when a transaction-related operation fails."""
    pass

class NetworkError(VernachainError):
    """Raised when network operations fail."""
    pass

class ValidationError(VernachainError):
    """Raised when data validation fails."""
    pass

class ContractError(VernachainError):
    """Raised when smart contract operations fail."""
    pass

class BridgeError(VernachainError):
    """Raised when cross-chain bridge operations fail."""
    pass

class AuthenticationError(VernachainError):
    """Raised when API authentication fails."""
    pass

class RateLimitError(VernachainError):
    """Raised when API rate limit is exceeded."""
    pass 