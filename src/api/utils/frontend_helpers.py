"""Frontend helper utilities for API integration."""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from pydantic import BaseModel
from fastapi import HTTPException
from fastapi.responses import JSONResponse


class APIResponse(BaseModel):
    """Standard API response model."""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    message: Optional[str] = None
    timestamp: datetime = datetime.utcnow()


def create_response(
    data: Any = None,
    message: Optional[str] = None,
    error: Optional[str] = None,
    status_code: int = 200,
) -> JSONResponse:
    """Create standardized API response."""
    response = APIResponse(
        success=error is None,
        data=data,
        error=error,
        message=message,
    )
    
    return JSONResponse(
        content=response.dict(),
        status_code=status_code,
    )


class PaginationParams(BaseModel):
    """Pagination parameters."""
    page: int = 1
    page_size: int = 10
    sort_by: Optional[str] = None
    sort_desc: bool = False


class PaginatedResponse(BaseModel):
    """Paginated response model."""
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


def paginate_response(
    items: List[Any],
    total: int,
    params: PaginationParams,
) -> Dict:
    """Create paginated response."""
    total_pages = (total + params.page_size - 1) // params.page_size
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=params.page,
        page_size=params.page_size,
        total_pages=total_pages,
        has_next=params.page < total_pages,
        has_prev=params.page > 1,
    ).dict()


class ErrorDetail(BaseModel):
    """Error detail model."""
    code: str
    message: str
    field: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


def create_error_response(
    message: str,
    code: str,
    status_code: int = 400,
    field: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> HTTPException:
    """Create standardized error response."""
    error_detail = ErrorDetail(
        code=code,
        message=message,
        field=field,
        details=details,
    )
    
    return HTTPException(
        status_code=status_code,
        detail=error_detail.dict(),
    )


class WebSocketMessage(BaseModel):
    """WebSocket message model."""
    type: str
    data: Any
    timestamp: datetime = datetime.utcnow()


def create_ws_message(
    type_: str,
    data: Any,
) -> Dict:
    """Create WebSocket message."""
    return WebSocketMessage(
        type=type_,
        data=data,
    ).dict()


# Frontend-specific error codes
ERROR_CODES = {
    "AUTH_REQUIRED": "Authentication required",
    "INVALID_CREDENTIALS": "Invalid credentials",
    "TOKEN_EXPIRED": "Token has expired",
    "PERMISSION_DENIED": "Permission denied",
    "RESOURCE_NOT_FOUND": "Resource not found",
    "VALIDATION_ERROR": "Validation error",
    "RATE_LIMIT_EXCEEDED": "Rate limit exceeded",
    "WALLET_ERROR": "Wallet operation error",
    "BLOCKCHAIN_ERROR": "Blockchain operation error",
    "NETWORK_ERROR": "Network error",
}


# Frontend helper functions
def format_blockchain_address(address: str, truncate: bool = True) -> str:
    """Format blockchain address for display."""
    if not address:
        return ""
    if truncate:
        return f"{address[:6]}...{address[-4:]}"
    return address


def format_token_amount(
    amount: Union[int, float],
    decimals: int = 18,
    include_suffix: bool = True,
) -> str:
    """Format token amount for display."""
    if amount is None:
        return "0"
    
    formatted = amount / (10 ** decimals)
    if formatted.is_integer():
        result = f"{int(formatted):,}"
    else:
        result = f"{formatted:,.6f}".rstrip("0").rstrip(".")
    
    return f"{result} ETH" if include_suffix else result


def format_timestamp(
    timestamp: Union[int, datetime],
    format_str: str = "%Y-%m-%d %H:%M:%S",
) -> str:
    """Format timestamp for display."""
    if isinstance(timestamp, int):
        timestamp = datetime.fromtimestamp(timestamp)
    return timestamp.strftime(format_str)


def create_explorer_link(
    hash_or_address: str,
    network: str = "mainnet",
    type_: str = "tx",
) -> str:
    """Create blockchain explorer link."""
    base_urls = {
        "mainnet": "https://etherscan.io",
        "ropsten": "https://ropsten.etherscan.io",
        "rinkeby": "https://rinkeby.etherscan.io",
        "goerli": "https://goerli.etherscan.io",
    }
    
    base_url = base_urls.get(network, base_urls["mainnet"])
    return f"{base_url}/{type_}/{hash_or_address}" 