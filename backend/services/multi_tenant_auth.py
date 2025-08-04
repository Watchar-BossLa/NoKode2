"""
Multi-Tenant Architecture with Enterprise SSO
JWT-based authentication with tenant isolation and SSO integration
"""
import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import uuid
import hashlib
import secrets
from dataclasses import dataclass, asdict
from enum import Enum
import jwt
import bcrypt
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
import httpx
from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

logger = logging.getLogger(__name__)

class UserRole(Enum):
    SUPER_ADMIN = "super_admin"
    TENANT_ADMIN = "tenant_admin"
    DEVELOPER = "developer"
    VIEWER = "viewer"

class TenantStatus(Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TRIAL = "trial"
    ENTERPRISE = "enterprise"

class SSOProvider(Enum):
    OKTA = "okta"
    AUTH0 = "auth0"
    AZURE_AD = "azure_ad"
    GOOGLE_WORKSPACE = "google_workspace"
    SAML = "saml"

@dataclass
class Tenant:
    id: str
    name: str
    domain: str
    status: TenantStatus
    created_at: datetime
    updated_at: datetime
    settings: Dict[str, Any]
    billing_tier: str
    max_users: int
    current_users: int
    sso_config: Optional[Dict[str, Any]] = None
    custom_branding: Optional[Dict[str, Any]] = None

@dataclass
class User:
    id: str
    email: str
    name: str
    tenant_id: str
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    password_hash: Optional[str] = None
    sso_provider: Optional[SSOProvider] = None
    sso_user_id: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None

@dataclass
class Session:
    id: str
    user_id: str
    tenant_id: str
    access_token: str
    refresh_token: str
    expires_at: datetime
    created_at: datetime
    ip_address: str
    user_agent: str
    is_active: bool

class MultiTenantAuthManager:
    def __init__(self, secret_key: str, redis_url: str = "redis://localhost:6379"):
        self.secret_key = secret_key
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7
        
        # In production, use proper database
        self.tenants: Dict[str, Tenant] = {}
        self.users: Dict[str, User] = {}
        self.sessions: Dict[str, Session] = {}
        
        # Initialize with default tenant
        self._create_default_tenant()
        
        # HTTP client for SSO providers
        self.http_client = httpx.AsyncClient(timeout=30.0)
        
        # Security settings
        self.max_login_attempts = 5
        self.lockout_duration_minutes = 15
        self.login_attempts: Dict[str, Dict] = {}  # email -> {attempts, last_attempt, locked_until}
    
    def _create_default_tenant(self):
        """Create default tenant for development"""
        default_tenant = Tenant(
            id="default",
            name="Default Organization",
            domain="localhost",
            status=TenantStatus.ENTERPRISE,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            settings={
                "allow_user_registration": True,
                "require_email_verification": False,
                "password_policy": {
                    "min_length": 8,
                    "require_uppercase": True,
                    "require_lowercase": True,
                    "require_numbers": True,
                    "require_symbols": False
                }
            },
            billing_tier="enterprise",
            max_users=1000,
            current_users=0
        )
        self.tenants["default"] = default_tenant
    
    async def create_tenant(self, tenant_data: Dict[str, Any]) -> Tenant:
        """Create a new tenant"""
        try:
            tenant_id = str(uuid.uuid4())
            tenant = Tenant(
                id=tenant_id,
                name=tenant_data["name"],
                domain=tenant_data["domain"],
                status=TenantStatus(tenant_data.get("status", "trial")),
                created_at=datetime.now(),
                updated_at=datetime.now(),
                settings=tenant_data.get("settings", {}),
                billing_tier=tenant_data.get("billing_tier", "starter"),
                max_users=tenant_data.get("max_users", 10),
                current_users=0,
                sso_config=tenant_data.get("sso_config"),
                custom_branding=tenant_data.get("custom_branding")
            )
            
            self.tenants[tenant_id] = tenant
            logger.info(f"Created tenant: {tenant.name} ({tenant_id})")
            return tenant
            
        except Exception as e:
            logger.error(f"Failed to create tenant: {e}")
            raise HTTPException(status_code=500, detail="Failed to create tenant")
    
    async def get_tenant_by_domain(self, domain: str) -> Optional[Tenant]:
        """Get tenant by domain"""
        for tenant in self.tenants.values():
            if tenant.domain == domain or domain.endswith(f".{tenant.domain}"):
                return tenant
        return None
    
    async def configure_sso(self, tenant_id: str, sso_config: Dict[str, Any]) -> bool:
        """Configure SSO for a tenant"""
        try:
            if tenant_id not in self.tenants:
                raise HTTPException(status_code=404, detail="Tenant not found")
            
            tenant = self.tenants[tenant_id]
            
            # Validate SSO configuration
            required_fields = {
                SSOProvider.OKTA: ["domain", "client_id", "client_secret"],
                SSOProvider.AUTH0: ["domain", "client_id", "client_secret"],
                SSOProvider.AZURE_AD: ["tenant_id", "client_id", "client_secret"],
                SSOProvider.GOOGLE_WORKSPACE: ["client_id", "client_secret", "hosted_domain"],
                SSOProvider.SAML: ["sso_url", "entity_id", "certificate"]
            }
            
            provider = SSOProvider(sso_config["provider"])
            for field in required_fields[provider]:
                if field not in sso_config:
                    raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
            
            tenant.sso_config = sso_config
            tenant.updated_at = datetime.now()
            
            logger.info(f"Configured SSO for tenant {tenant_id}: {provider.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to configure SSO: {e}")
            raise
    
    async def register_user(self, tenant_id: str, user_data: Dict[str, Any]) -> User:
        """Register a new user"""
        try:
            tenant = self.tenants.get(tenant_id)
            if not tenant:
                raise HTTPException(status_code=404, detail="Tenant not found")
            
            if tenant.current_users >= tenant.max_users:
                raise HTTPException(status_code=400, detail="Tenant user limit reached")
            
            # Check if user already exists
            email = user_data["email"].lower()
            for user in self.users.values():
                if user.email == email and user.tenant_id == tenant_id:
                    raise HTTPException(status_code=400, detail="User already exists")
            
            # Validate password policy
            if "password" in user_data and not self._validate_password(user_data["password"], tenant.settings.get("password_policy", {})):
                raise HTTPException(status_code=400, detail="Password does not meet policy requirements")
            
            user_id = str(uuid.uuid4())
            password_hash = None
            if "password" in user_data:
                password_hash = self._hash_password(user_data["password"])
            
            user = User(
                id=user_id,
                email=email,
                name=user_data["name"],
                tenant_id=tenant_id,
                role=UserRole(user_data.get("role", "developer")),
                is_active=True,
                is_verified=not tenant.settings.get("require_email_verification", False),
                created_at=datetime.now(),
                updated_at=datetime.now(),
                password_hash=password_hash,
                preferences=user_data.get("preferences", {})
            )
            
            self.users[user_id] = user
            tenant.current_users += 1
            
            logger.info(f"Registered user: {email} in tenant {tenant_id}")
            return user
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to register user: {e}")
            raise HTTPException(status_code=500, detail="Failed to register user")
    
    async def authenticate_user(self, tenant_id: str, email: str, password: str, ip_address: str, user_agent: str) -> Dict[str, Any]:
        """Authenticate user with email/password"""
        try:
            # Check rate limiting
            if self._is_rate_limited(email):
                raise HTTPException(status_code=429, detail="Too many login attempts. Please try again later.")
            
            # Find user
            user = None
            for u in self.users.values():
                if u.email == email.lower() and u.tenant_id == tenant_id:
                    user = u
                    break
            
            if not user or not user.is_active:
                self._record_failed_attempt(email)
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            # Verify password
            if not user.password_hash or not self._verify_password(password, user.password_hash):
                self._record_failed_attempt(email)
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            # Reset failed attempts on successful login
            if email in self.login_attempts:
                del self.login_attempts[email]
            
            # Create session
            session = await self._create_session(user, ip_address, user_agent)
            
            # Update last login
            user.last_login = datetime.now()
            user.updated_at = datetime.now()
            
            return {
                "access_token": session.access_token,
                "refresh_token": session.refresh_token,
                "token_type": "bearer",
                "expires_in": self.access_token_expire_minutes * 60,
                "user": self._serialize_user(user)
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise HTTPException(status_code=500, detail="Authentication failed")
    
    async def sso_authenticate(self, tenant_id: str, provider: str, auth_code: str, redirect_uri: str, ip_address: str, user_agent: str) -> Dict[str, Any]:
        """Authenticate user via SSO"""
        try:
            tenant = self.tenants.get(tenant_id)
            if not tenant or not tenant.sso_config:
                raise HTTPException(status_code=400, detail="SSO not configured for tenant")
            
            sso_provider = SSOProvider(provider)
            
            # Exchange auth code for user info
            user_info = await self._exchange_sso_code(tenant.sso_config, sso_provider, auth_code, redirect_uri)
            
            # Find or create user
            user = await self._find_or_create_sso_user(tenant_id, user_info, sso_provider)
            
            # Create session
            session = await self._create_session(user, ip_address, user_agent)
            
            # Update last login
            user.last_login = datetime.now()
            user.updated_at = datetime.now()
            
            return {
                "access_token": session.access_token,
                "refresh_token": session.refresh_token,
                "token_type": "bearer",
                "expires_in": self.access_token_expire_minutes * 60,
                "user": self._serialize_user(user)
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"SSO authentication failed: {e}")
            raise HTTPException(status_code=500, detail="SSO authentication failed")
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token"""
        try:
            # Find session by refresh token
            session = None
            for s in self.sessions.values():
                if s.refresh_token == refresh_token and s.is_active:
                    session = s
                    break
            
            if not session or session.expires_at < datetime.now():
                raise HTTPException(status_code=401, detail="Invalid refresh token")
            
            # Get user
            user = self.users.get(session.user_id)
            if not user or not user.is_active:
                raise HTTPException(status_code=401, detail="User not found or inactive")
            
            # Create new access token
            access_token = self._create_access_token(user)
            session.access_token = access_token
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": self.access_token_expire_minutes * 60
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            raise HTTPException(status_code=500, detail="Token refresh failed")
    
    async def logout(self, access_token: str):
        """Logout user and invalidate session"""
        try:
            payload = jwt.decode(access_token, self.secret_key, algorithms=[self.algorithm])
            session_id = payload.get("session_id")
            
            if session_id and session_id in self.sessions:
                self.sessions[session_id].is_active = False
                logger.info(f"User logged out: {payload.get('sub')}")
            
        except Exception as e:
            logger.error(f"Logout failed: {e}")
    
    async def get_current_user(self, token: str) -> User:
        """Get current user from access token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id = payload.get("sub")
            session_id = payload.get("session_id")
            
            if not user_id or not session_id:
                raise HTTPException(status_code=401, detail="Invalid token")
            
            # Check session
            session = self.sessions.get(session_id)
            if not session or not session.is_active or session.expires_at < datetime.now():
                raise HTTPException(status_code=401, detail="Session expired")
            
            # Get user
            user = self.users.get(user_id)
            if not user or not user.is_active:
                raise HTTPException(status_code=401, detail="User not found or inactive")
            
            return user
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get current user: {e}")
            raise HTTPException(status_code=401, detail="Authentication failed")
    
    def require_role(self, required_role: UserRole):
        """Decorator to require specific role"""
        def role_checker(user: User) -> User:
            role_hierarchy = {
                UserRole.VIEWER: 1,
                UserRole.DEVELOPER: 2,
                UserRole.TENANT_ADMIN: 3,
                UserRole.SUPER_ADMIN: 4
            }
            
            if role_hierarchy.get(user.role, 0) < role_hierarchy.get(required_role, 0):
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            return user
        
        return role_checker
    
    async def _create_session(self, user: User, ip_address: str, user_agent: str) -> Session:
        """Create a new user session"""
        session_id = str(uuid.uuid4())
        access_token = self._create_access_token(user, session_id)
        refresh_token = self._create_refresh_token(user, session_id)
        
        session = Session(
            id=session_id,
            user_id=user.id,
            tenant_id=user.tenant_id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=datetime.now() + timedelta(days=self.refresh_token_expire_days),
            created_at=datetime.now(),
            ip_address=ip_address,
            user_agent=user_agent,
            is_active=True
        )
        
        self.sessions[session_id] = session
        return session
    
    def _create_access_token(self, user: User, session_id: str = None) -> str:
        """Create JWT access token"""
        now = datetime.now()
        expire = now + timedelta(minutes=self.access_token_expire_minutes)
        
        payload = {
            "sub": user.id,
            "email": user.email,
            "tenant_id": user.tenant_id,
            "role": user.role.value,
            "iat": now.timestamp(),
            "exp": expire.timestamp(),
            "session_id": session_id
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def _create_refresh_token(self, user: User, session_id: str) -> str:
        """Create JWT refresh token"""
        now = datetime.now()
        expire = now + timedelta(days=self.refresh_token_expire_days)
        
        payload = {
            "sub": user.id,
            "session_id": session_id,
            "type": "refresh",
            "iat": now.timestamp(),
            "exp": expire.timestamp()
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def _validate_password(self, password: str, policy: Dict[str, Any]) -> bool:
        """Validate password against policy"""
        if len(password) < policy.get("min_length", 8):
            return False
        
        if policy.get("require_uppercase", False) and not any(c.isupper() for c in password):
            return False
        
        if policy.get("require_lowercase", False) and not any(c.islower() for c in password):
            return False
        
        if policy.get("require_numbers", False) and not any(c.isdigit() for c in password):
            return False
        
        if policy.get("require_symbols", False) and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            return False
        
        return True
    
    def _is_rate_limited(self, email: str) -> bool:
        """Check if email is rate limited"""
        if email not in self.login_attempts:
            return False
        
        attempts = self.login_attempts[email]
        
        # Check if still locked out
        if "locked_until" in attempts and attempts["locked_until"] > datetime.now():
            return True
        
        return False
    
    def _record_failed_attempt(self, email: str):
        """Record failed login attempt"""
        now = datetime.now()
        
        if email not in self.login_attempts:
            self.login_attempts[email] = {"attempts": 0, "last_attempt": now}
        
        attempts_data = self.login_attempts[email]
        attempts_data["attempts"] += 1
        attempts_data["last_attempt"] = now
        
        # Lock account if too many attempts
        if attempts_data["attempts"] >= self.max_login_attempts:
            attempts_data["locked_until"] = now + timedelta(minutes=self.lockout_duration_minutes)
            logger.warning(f"Account locked due to too many failed attempts: {email}")
    
    async def _exchange_sso_code(self, sso_config: Dict[str, Any], provider: SSOProvider, auth_code: str, redirect_uri: str) -> Dict[str, Any]:
        """Exchange SSO authorization code for user information"""
        try:
            if provider == SSOProvider.OKTA:
                return await self._okta_exchange_code(sso_config, auth_code, redirect_uri)
            elif provider == SSOProvider.AUTH0:
                return await self._auth0_exchange_code(sso_config, auth_code, redirect_uri)
            elif provider == SSOProvider.AZURE_AD:
                return await self._azure_ad_exchange_code(sso_config, auth_code, redirect_uri)
            elif provider == SSOProvider.GOOGLE_WORKSPACE:
                return await self._google_workspace_exchange_code(sso_config, auth_code, redirect_uri)
            else:
                raise HTTPException(status_code=400, detail="Unsupported SSO provider")
                
        except Exception as e:
            logger.error(f"SSO code exchange failed: {e}")
            raise HTTPException(status_code=400, detail="SSO authentication failed")
    
    async def _okta_exchange_code(self, config: Dict[str, Any], code: str, redirect_uri: str) -> Dict[str, Any]:
        """Exchange Okta authorization code"""
        token_url = f"https://{config['domain']}/oauth2/default/v1/token"
        userinfo_url = f"https://{config['domain']}/oauth2/default/v1/userinfo"
        
        # Exchange code for token
        token_response = await self.http_client.post(token_url, data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": config["client_id"],
            "client_secret": config["client_secret"]
        })
        token_response.raise_for_status()
        token_data = token_response.json()
        
        # Get user info
        user_response = await self.http_client.get(
            userinfo_url,
            headers={"Authorization": f"Bearer {token_data['access_token']}"}
        )
        user_response.raise_for_status()
        
        return user_response.json()
    
    async def _auth0_exchange_code(self, config: Dict[str, Any], code: str, redirect_uri: str) -> Dict[str, Any]:
        """Exchange Auth0 authorization code"""
        token_url = f"https://{config['domain']}/oauth/token"
        userinfo_url = f"https://{config['domain']}/userinfo"
        
        # Exchange code for token
        token_response = await self.http_client.post(token_url, json={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": config["client_id"],
            "client_secret": config["client_secret"]
        })
        token_response.raise_for_status()
        token_data = token_response.json()
        
        # Get user info
        user_response = await self.http_client.get(
            userinfo_url,
            headers={"Authorization": f"Bearer {token_data['access_token']}"}
        )
        user_response.raise_for_status()
        
        return user_response.json()
    
    async def _azure_ad_exchange_code(self, config: Dict[str, Any], code: str, redirect_uri: str) -> Dict[str, Any]:
        """Exchange Azure AD authorization code"""
        token_url = f"https://login.microsoftonline.com/{config['tenant_id']}/oauth2/v2.0/token"
        
        # Exchange code for token
        token_response = await self.http_client.post(token_url, data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "scope": "openid profile email"
        })
        token_response.raise_for_status()
        token_data = token_response.json()
        
        # Decode ID token to get user info
        id_token = token_data["id_token"]
        # Note: In production, verify the JWT signature
        payload = jwt.decode(id_token, options={"verify_signature": False})
        
        return payload
    
    async def _google_workspace_exchange_code(self, config: Dict[str, Any], code: str, redirect_uri: str) -> Dict[str, Any]:
        """Exchange Google Workspace authorization code"""
        token_url = "https://oauth2.googleapis.com/token"
        userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        
        # Exchange code for token
        token_response = await self.http_client.post(token_url, data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": config["client_id"],
            "client_secret": config["client_secret"]
        })
        token_response.raise_for_status()
        token_data = token_response.json()
        
        # Get user info
        user_response = await self.http_client.get(
            userinfo_url,
            headers={"Authorization": f"Bearer {token_data['access_token']}"}
        )
        user_response.raise_for_status()
        user_data = user_response.json()
        
        # Verify hosted domain
        if config.get("hosted_domain") and user_data.get("hd") != config["hosted_domain"]:
            raise HTTPException(status_code=403, detail="User not from allowed domain")
        
        return user_data
    
    async def _find_or_create_sso_user(self, tenant_id: str, user_info: Dict[str, Any], provider: SSOProvider) -> User:
        """Find or create user from SSO information"""
        email = user_info.get("email", "").lower()
        name = user_info.get("name", "") or user_info.get("given_name", "") + " " + user_info.get("family_name", "")
        sso_user_id = user_info.get("sub") or user_info.get("oid") or user_info.get("id")
        
        # Find existing user
        for user in self.users.values():
            if user.email == email and user.tenant_id == tenant_id:
                # Update SSO info if not set
                if not user.sso_provider:
                    user.sso_provider = provider
                    user.sso_user_id = sso_user_id
                    user.updated_at = datetime.now()
                return user
        
        # Create new user
        user_id = str(uuid.uuid4())
        user = User(
            id=user_id,
            email=email,
            name=name.strip(),
            tenant_id=tenant_id,
            role=UserRole.DEVELOPER,  # Default role for SSO users
            is_active=True,
            is_verified=True,  # SSO users are pre-verified
            created_at=datetime.now(),
            updated_at=datetime.now(),
            sso_provider=provider,
            sso_user_id=sso_user_id
        )
        
        self.users[user_id] = user
        
        # Update tenant user count
        if tenant_id in self.tenants:
            self.tenants[tenant_id].current_users += 1
        
        logger.info(f"Created SSO user: {email} via {provider.value}")
        return user
    
    def _serialize_user(self, user: User) -> Dict[str, Any]:
        """Serialize user for API response"""
        return {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "tenant_id": user.tenant_id,
            "role": user.role.value,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "created_at": user.created_at.isoformat(),
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "sso_provider": user.sso_provider.value if user.sso_provider else None,
            "preferences": user.preferences
        }

# Global auth manager instance
auth_manager = MultiTenantAuthManager(
    secret_key=os.getenv("JWT_SECRET_KEY", "your-super-secret-jwt-key-change-in-production"),
    redis_url=os.getenv("REDIS_URL", "redis://localhost:6379")
)

# FastAPI dependencies
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """FastAPI dependency to get current user"""
    return await auth_manager.get_current_user(credentials.credentials)

async def get_current_tenant(request: Request) -> Tenant:
    """FastAPI dependency to get current tenant from request"""
    host = request.headers.get("host", "localhost")
    domain = host.split(":")[0]  # Remove port if present
    
    tenant = await auth_manager.get_tenant_by_domain(domain)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    return tenant

def require_role(role: UserRole):
    """FastAPI dependency factory to require specific role"""
    def role_dependency(user: User = Depends(get_current_user)) -> User:
        return auth_manager.require_role(role)(user)
    return role_dependency