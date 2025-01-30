"""Authentication service for managing users and sessions."""

import bcrypt
import jwt
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
import logging
from eth_account import Account
from eth_account.messages import encode_defunct
from web3 import Web3
from web3.types import ChecksumAddress
import geoip2.database
import user_agents
from cryptography.fernet import Fernet
from webauthn import (
    generate_registration_options,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response,
)
from webauthn.helpers.cose import COSEAlgorithmIdentifier
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    UserVerificationRequirement,
    AttestationConveyancePreference,
)

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

logger = logging.getLogger(__name__)

class AuthService:
    """Service for handling user authentication and management."""
    
    def __init__(
        self,
        jwt_secret: str,
        encryption_key: str,
        session_duration: int = 3600,
        max_failed_attempts: int = 5,
        lockout_duration: int = 300,
        geoip_db_path: Optional[str] = None,
    ):
        """Initialize auth service."""
        self.jwt_secret = jwt_secret
        self.fernet = Fernet(encryption_key.encode())
        self.session_duration = session_duration
        self.max_failed_attempts = max_failed_attempts
        self.lockout_duration = lockout_duration
        self.geoip_reader = (
            geoip2.database.Reader(geoip_db_path) if geoip_db_path else None
        )
        self.web3 = Web3()
        
    async def register_user(
        self,
        email: str,
        password: Optional[str] = None,
        roles: Optional[List[UserRole]] = None,
        security_settings: Optional[SecuritySettings] = None,
        auth_method: AuthMethod = AuthMethod.PASSWORD,
    ) -> User:
        """Register a new user."""
        user = User(
            email=email,
            roles=set(roles) if roles else {UserRole.USER},
            security_settings=security_settings or SecuritySettings(),
        )
        
        if auth_method == AuthMethod.PASSWORD and password:
            user.password_hash = self._hash_password(password)
        
        await self._create_audit_log(
            user.id,
            "user_registration",
            "success",
            {"auth_method": auth_method.value},
        )
        return user
        
    async def authenticate_user(
        self,
        email: str,
        password: Optional[str] = None,
        wallet_signature: Optional[str] = None,
        webauthn_response: Optional[Dict] = None,
        ip_address: Optional[str] = None,
        user_agent_string: Optional[str] = None,
    ) -> Tuple[Optional[User], Optional[Session]]:
        """Authenticate user with various methods."""
        user = await self._get_user_by_email(email)
        if not user or not user.is_active:
            return None, None
            
        if user.locked_until and user.locked_until > datetime.utcnow():
            await self._create_audit_log(
                user.id,
                "authentication_attempt",
                "failed",
                {"reason": "account_locked"},
            )
            return None, None
            
        auth_success = False
        auth_method = None
        
        if password and AuthMethod.PASSWORD in user.security_settings.allowed_auth_methods:
            auth_success = self._verify_password(password, user.password_hash)
            auth_method = AuthMethod.PASSWORD
            
        elif wallet_signature and AuthMethod.HARDWARE_WALLET in user.security_settings.allowed_auth_methods:
            auth_success = self._verify_wallet_signature(user, wallet_signature)
            auth_method = AuthMethod.HARDWARE_WALLET
            
        elif webauthn_response and AuthMethod.HARDWARE_KEY in user.security_settings.allowed_auth_methods:
            auth_success = await self._verify_webauthn(user, webauthn_response)
            auth_method = AuthMethod.HARDWARE_KEY
            
        if not auth_success:
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= self.max_failed_attempts:
                user.locked_until = datetime.utcnow() + timedelta(seconds=self.lockout_duration)
            await self._create_audit_log(
                user.id,
                "authentication_attempt",
                "failed",
                {"method": auth_method.value if auth_method else None},
            )
            return None, None
            
        # Reset failed attempts on successful login
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login = datetime.utcnow()
        
        # Create session with enhanced security
        session = await self._create_session(
            user,
            auth_method,
            ip_address,
            user_agent_string,
        )
        
        await self._create_audit_log(
            user.id,
            "authentication_attempt",
            "success",
            {"method": auth_method.value, "session_id": session.id},
        )
        
        return user, session
    
    async def verify_session(
        self,
        session_id: str,
        token: str,
        fingerprint: Optional[str] = None,
    ) -> Optional[Session]:
        """Verify session with enhanced security checks."""
        session = await self._get_session(session_id)
        if not session or not session.is_active or session.is_expired():
            return None
            
        if fingerprint and not session.fingerprint == fingerprint:
            await self._create_audit_log(
                session.user_id,
                "session_verification",
                "failed",
                {"reason": "fingerprint_mismatch"},
            )
            return None
            
        if session.token != token:
            await self._create_audit_log(
                session.user_id,
                "session_verification",
                "failed",
                {"reason": "invalid_token"},
            )
            return None
            
        session.update_activity()
        return session
    
    async def add_hardware_wallet(
        self,
        user: User,
        address: ChecksumAddress,
        encrypted_private_key: Optional[str] = None,
        hardware_path: Optional[str] = None,
        label: Optional[str] = None,
    ) -> None:
        """Add hardware wallet to user account."""
        wallet_config = WalletConfig(
            address=address,
            wallet_type=WalletType.HARDWARE if hardware_path else WalletType.SOFTWARE,
            encrypted_private_key=encrypted_private_key,
            hardware_path=hardware_path,
            label=label,
        )
        user.add_wallet(wallet_config)
        await self._create_audit_log(
            user.id,
            "wallet_added",
            "success",
            {"address": address, "type": wallet_config.wallet_type.value},
        )
    
    async def setup_webauthn(self, user: User) -> Dict:
        """Set up WebAuthn for user."""
        options = generate_registration_options(
            rp_id="yourdomain.com",
            rp_name="Your Service",
            user_id=user.id,
            user_name=user.email,
            authenticator_selection=AuthenticatorSelectionCriteria(
                user_verification=UserVerificationRequirement.PREFERRED,
            ),
            attestation=AttestationConveyancePreference.DIRECT,
        )
        return options
    
    async def verify_webauthn_registration(
        self,
        user: User,
        response: Dict,
    ) -> bool:
        """Verify WebAuthn registration response."""
        try:
            credential = verify_registration_response(
                credential=response,
                expected_challenge=response["challenge"],
                expected_origin="https://yourdomain.com",
                expected_rp_id="yourdomain.com",
            )
            user.add_webauthn_credential(credential.json())
            await self._create_audit_log(
                user.id,
                "webauthn_registration",
                "success",
                {"credential_id": credential.credential_id},
            )
            return True
        except Exception as e:
            logger.error(f"WebAuthn registration failed: {str(e)}")
            await self._create_audit_log(
                user.id,
                "webauthn_registration",
                "failed",
                {"error": str(e)},
            )
        return False
        
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash."""
        return bcrypt.checkpw(password.encode(), password_hash.encode())
    
    def _verify_wallet_signature(self, user: User, signature: str) -> bool:
        """Verify wallet signature."""
        try:
            message = f"Login to service at {datetime.utcnow().date()}"
            message_hash = encode_defunct(text=message)
            address = Account.recover_message(message_hash, signature=signature)
            return any(w.address == address for w in user.wallets)
        except Exception as e:
            logger.error(f"Wallet signature verification failed: {str(e)}")
            return False
    
    async def _create_session(
        self,
        user: User,
        auth_method: AuthMethod,
        ip_address: Optional[str] = None,
        user_agent_string: Optional[str] = None,
    ) -> Session:
        """Create new session with enhanced security."""
        expires_at = datetime.utcnow() + timedelta(seconds=self.session_duration)
        fingerprint = secrets.token_hex(32)
        
        # Parse user agent
        device_info = {}
        if user_agent_string:
            ua = user_agents.parse(user_agent_string)
            device_info = {
                "browser": ua.browser.family,
                "os": ua.os.family,
                "device": ua.device.family,
            }
        
        # Get geolocation
        geo_location = None
        if ip_address and self.geoip_reader:
            try:
                response = self.geoip_reader.city(ip_address)
                geo_location = {
                    "country": response.country.name,
                    "city": response.city.name,
                    "latitude": response.location.latitude,
                    "longitude": response.location.longitude,
                }
            except Exception as e:
                logger.error(f"Geolocation lookup failed: {str(e)}")
        
        session = Session(
            user_id=user.id,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent_string,
            fingerprint=fingerprint,
            auth_method=auth_method,
            device_info=device_info,
            geo_location=geo_location,
        )
        
        user.add_session_fingerprint(fingerprint)
        return session
    
    async def _create_audit_log(
        self,
        user_id: str,
        action: str,
        status: str,
        details: Dict = None,
    ) -> None:
        """Create audit log entry."""
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            status=status,
            details=details or {},
        )
        # Save audit log to database
        logger.info(f"Audit log created: {audit_log}")
    
    async def _get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email from database."""
        # Implementation depends on your database
        pass
    
    async def _get_session(self, session_id: str) -> Optional[Session]:
        """Get session from database."""
        # Implementation depends on your database
        pass 