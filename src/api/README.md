# Vernachain API Service

A FastAPI-based RESTful API service for the Vernachain blockchain platform.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.95.0+-blue.svg)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.12.4+-blue.svg)](https://www.python.org/downloads/)
[![OpenAPI](https://img.shields.io/badge/OpenAPI-3.0.3-green.svg)](https://swagger.io/specification/)
[![JWT](https://img.shields.io/badge/JWT-Auth-orange.svg)](https://jwt.io/)

## Overview

The API service provides a comprehensive interface for interacting with the Vernachain blockchain, including:
- Account management
- Token operations
- Smart contract interactions
- Network statistics
- Transaction processing

## 🚀 Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the API service:
```bash
# Development mode
python start.py --dev

# Production mode
uvicorn src.api.service:app --host 0.0.0.0 --port 8000
```

3. Access the API documentation:
- OpenAPI UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📚 API Endpoints

### Authentication
```
POST   /api/v1/auth/login            # User login
POST   /api/v1/auth/register         # User registration
POST   /api/v1/auth/logout           # User logout
POST   /api/v1/auth/reset-password   # Password reset request
POST   /api/v1/auth/verify-2fa       # 2FA verification
```

### Token Management
```
POST   /api/v1/tokens/create         # Create new token
GET    /api/v1/tokens                # List all tokens
GET    /api/v1/tokens/{id}           # Get token details
POST   /api/v1/tokens/transfer       # Transfer tokens
POST   /api/v1/tokens/burn           # Burn tokens
POST   /api/v1/tokens/mint           # Mint new tokens
```

### Blockchain Operations
```
GET    /api/v1/stats                 # Network statistics
GET    /api/v1/blocks                # List blocks
GET    /api/v1/block/{number}        # Get block details
GET    /api/v1/transactions          # List transactions
GET    /api/v1/transaction/{hash}    # Get transaction details
```

### Account Management
```
GET    /api/v1/address/{address}     # Get address info
GET    /api/v1/address/{address}/transactions  # Get address transactions
POST   /api/v1/address/create        # Create new address
```

## 🔒 Authentication

The API uses JWT (JSON Web Tokens) for authentication:

1. **Login Flow**:
```python
response = requests.post("/api/v1/auth/login", json={
    "email": "user@example.com",
    "password": "secure_password"
})
token = response.json()["token"]
```

2. **Using the Token**:
```python
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
response = requests.get("/api/v1/tokens", headers=headers)
```

## 🛠️ Development

### Project Structure
```
api/
├── __init__.py
├── service.py          # Main FastAPI application
├── models.py           # Pydantic models
├── routes/            # API route handlers
│   ├── auth.py
│   ├── tokens.py
│   └── blockchain.py
├── middleware/        # Custom middleware
│   ├── auth.py
│   └── cors.py
└── utils/            # Utility functions
    ├── validation.py
    └── security.py
```

### Adding New Endpoints

1. Create route handler:
```python
from fastapi import APIRouter, Depends
from ..models import ResponseModel

router = APIRouter()

@router.get("/endpoint")
async def handler() -> ResponseModel:
    return {"data": "response"}
```

2. Register in `service.py`:
```python
from .routes import new_router
app.include_router(new_router, prefix="/api/v1")
```

## 📊 Response Format

All API responses follow a standard format:

### Success Response
```json
{
    "success": true,
    "data": {
        // Response data
    },
    "message": "Optional success message"
}
```

### Error Response
```json
{
    "success": false,
    "error": {
        "code": "ERROR_CODE",
        "message": "Error description"
    }
}
```

## ⚙️ Configuration

### Environment Variables
```env
API_HOST=localhost
API_PORT=8000
JWT_SECRET=your-secret-key
DATABASE_URL=postgresql://user:pass@localhost/db
DEBUG=True
```

### CORS Configuration
```python
origins = [
    "http://localhost:5173",  # Frontend dev server
    "http://localhost:8001",  # Explorer backend
]
```

## 🔧 Error Handling

Common error codes and their meanings:

| Code | Description |
|------|-------------|
| AUTH001 | Authentication failed |
| AUTH002 | Token expired |
| TOKEN001 | Invalid token operation |
| CHAIN001 | Blockchain error |
| VAL001 | Validation error |

## 🧪 Testing

1. Run tests:
```bash
pytest tests/api/
```

2. Run with coverage:
```bash
pytest --cov=src/api tests/api/
```

## 📈 Performance

### Rate Limiting
- 100 requests per minute for authenticated users
- 20 requests per minute for unauthenticated users
- Configurable per endpoint

### Caching
- Response caching for frequently accessed data
- Redis cache backend
- Configurable TTL per endpoint

## 🔐 Security

### Headers
```python
security_headers = {
    "X-Frame-Options": "DENY",
    "X-Content-Type-Options": "nosniff",
    "X-XSS-Protection": "1; mode=block",
    "Content-Security-Policy": "default-src 'self'"
}
```

### Input Validation
- All inputs validated using Pydantic models
- Strict type checking
- Custom validation rules

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [API Design Guidelines](docs/api-guidelines.md)
- [Authentication Flow](docs/auth-flow.md)
- [Deployment Guide](docs/deployment.md)

## 🐛 Troubleshooting

1. **Connection Issues**
   - Verify service is running
   - Check port availability
   - Verify network connectivity

2. **Authentication Issues**
   - Check token expiration
   - Verify credentials
   - Check JWT secret

3. **Performance Issues**
   - Monitor rate limits
   - Check cache configuration
   - Review database queries

## 🤝 Contributing

1. Follow API design guidelines
2. Add tests for new endpoints
3. Update documentation
4. Follow security best practices

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for more details. 