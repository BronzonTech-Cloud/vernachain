"""
Authentication module for Vernachain.

This module handles user authentication, session management, and 2FA.
"""

from .models import (
    User,
    Session,
    AuthMethod,
    UserRole,
    WalletType,
    WalletConfig,
    SecuritySettings,
    AuditLog,
)
from .service import AuthService
from .utils import SecurityUtils

__all__ = [
    'User',
    'Session',
    'AuthMethod',
    'UserRole',
    'WalletType',
    'WalletConfig',
    'SecuritySettings',
    'AuditLog',
    'AuthService',
    'SecurityUtils',
] 