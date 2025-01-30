"""Models for authentication system."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Set
from enum import Enum
import secrets
import pyotp
import json
from web3.types import ChecksumAddress


class AuthMethod(Enum):
    """Authentication methods supported by the system."""
    PASSWORD = "password"
    HARDWARE_WALLET = "hardware_wallet"
    HARDWARE_KEY = "hardware_key"
    OAUTH = "oauth"
    SSO = "sso"


class UserRole(Enum):
    """User roles for role-based access control."""
    ADMIN = "admin"
    OPERATOR = "operator"
    USER = "user"
    AUDITOR = "auditor"


class WalletType(Enum):
    """Types of wallets supported by the system."""
    SOFTWARE = "software"
    HARDWARE = "hardware"
    MULTISIG = "multisig"


@dataclass
class SecuritySettings:
    """Security settings for user account."""
    ip_whitelist: List[str] = field(default_factory=list)
    allowed_countries: List[str] = field(default_factory=list)
    max_devices: int = 5
    require_2fa: bool = False
    allowed_auth_methods: List[AuthMethod] = field(default_factory=lambda: [AuthMethod.PASSWORD])
    transaction_limit_daily: float = 0
    transaction_limit_single: float = 0
    require_email_verification: bool = True


@dataclass
class WalletConfig:
    """Wallet configuration for user."""
    address: ChecksumAddress
    wallet_type: WalletType
    encrypted_private_key: Optional[str] = None
    hardware_path: Optional[str] = None
    multisig_threshold: Optional[int] = None
    multisig_owners: List[ChecksumAddress] = field(default_factory=list)
    is_active: bool = True
    label: Optional[str] = None


@dataclass
class AuditLog:
    """Audit log entry."""
    id: str = field(default_factory=lambda: secrets.token_hex(16))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    user_id: str
    action: str
    status: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    details: Dict = field(default_factory=dict)


@dataclass
class User:
    """User model for authentication."""
    id: str = field(default_factory=lambda: secrets.token_hex(16))
    email: str
    password_hash: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    two_factor_enabled: bool = False
    two_factor_secret: Optional[str] = None
    api_keys: List[str] = field(default_factory=list)
    is_active: bool = True
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    roles: Set[UserRole] = field(default_factory=lambda: {UserRole.USER})
    security_settings: SecuritySettings = field(default_factory=SecuritySettings)
    wallets: List[WalletConfig] = field(default_factory=list)
    oauth_providers: Dict[str, Dict] = field(default_factory=dict)
    sso_config: Optional[Dict] = None
    webauthn_credentials: List[Dict] = field(default_factory=list)
    session_fingerprints: List[str] = field(default_factory=list)
    
    def enable_2fa(self) -> str:
        """Enable 2FA for user and return secret."""
        self.two_factor_secret = pyotp.random_base32()
        self.two_factor_enabled = True
        self.security_settings.require_2fa = True
        self.updated_at = datetime.utcnow()
        return self.two_factor_secret
    
    def verify_2fa(self, code: str) -> bool:
        """Verify 2FA code."""
        if not self.two_factor_enabled or not self.two_factor_secret:
            return False
        totp = pyotp.TOTP(self.two_factor_secret)
        return totp.verify(code)
    
    def add_wallet(self, wallet: WalletConfig) -> None:
        """Add wallet configuration."""
        self.wallets.append(wallet)
        self.updated_at = datetime.utcnow()
    
    def remove_wallet(self, address: ChecksumAddress) -> None:
        """Remove wallet configuration."""
        self.wallets = [w for w in self.wallets if w.address != address]
        self.updated_at = datetime.utcnow()
    
    def add_webauthn_credential(self, credential: Dict) -> None:
        """Add WebAuthn credential."""
        self.webauthn_credentials.append(credential)
        self.updated_at = datetime.utcnow()
    
    def verify_session_fingerprint(self, fingerprint: str) -> bool:
        """Verify session fingerprint."""
        return fingerprint in self.session_fingerprints
    
    def add_session_fingerprint(self, fingerprint: str) -> None:
        """Add session fingerprint."""
        if len(self.session_fingerprints) >= self.security_settings.max_devices:
            self.session_fingerprints.pop(0)
        self.session_fingerprints.append(fingerprint)
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission."""
        permission_map = {
            "admin": {UserRole.ADMIN},
            "operate": {UserRole.ADMIN, UserRole.OPERATOR},
            "audit": {UserRole.ADMIN, UserRole.AUDITOR},
            "transact": {UserRole.ADMIN, UserRole.OPERATOR, UserRole.USER}
        }
        required_roles = permission_map.get(permission, set())
        return bool(required_roles & self.roles)
    
    def to_dict(self) -> Dict:
        """Convert user to dictionary."""
        return {
            "id": self.id,
            "email": self.email,
            "is_active": self.is_active,
            "roles": [role.value for role in self.roles],
            "two_factor_enabled": self.two_factor_enabled,
            "wallets": [
                {
                    "address": w.address,
                    "type": w.wallet_type.value,
                    "label": w.label
                }
                for w in self.wallets
            ],
            "security_settings": {
                "ip_whitelist": self.security_settings.ip_whitelist,
                "allowed_countries": self.security_settings.allowed_countries,
                "require_2fa": self.security_settings.require_2fa,
                "transaction_limit_daily": self.security_settings.transaction_limit_daily
            }
        }


@dataclass
class Session:
    """Session model for user authentication."""
    id: str = field(default_factory=lambda: secrets.token_hex(32))
    user_id: str
    token: str = field(default_factory=lambda: secrets.token_hex(64))
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime
    is_active: bool = True
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    last_activity: datetime = field(default_factory=datetime.utcnow)
    fingerprint: Optional[str] = None
    auth_method: AuthMethod = AuthMethod.PASSWORD
    device_info: Dict = field(default_factory=dict)
    geo_location: Optional[Dict] = None
    
    def is_expired(self) -> bool:
        """Check if session is expired."""
        return datetime.utcnow() > self.expires_at
    
    def update_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_activity = datetime.utcnow()
    
    def to_dict(self) -> Dict:
        """Convert session to dictionary."""
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "auth_method": self.auth_method.value,
            "device_info": self.device_info,
            "geo_location": self.geo_location
        } 