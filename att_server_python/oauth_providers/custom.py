"""
Custom OAuth Provider with Persistent Storage

OAuth provider with persistent client registration and refresh tokens.
Authorization codes and access tokens are kept in memory (short-lived).
"""

import secrets
import time
import logging
from dataclasses import dataclass, field
from typing import Dict, Optional, List
from urllib.parse import urlencode

from mcp.shared.auth import OAuthClientInformationFull, OAuthToken
from mcp.server.auth.provider import (
    AuthorizationParams,
    AuthorizationCode,
    RefreshToken,
    AccessToken,
    AuthorizeError,
    construct_redirect_uri,
)

from .base import BaseOAuthProvider, ProviderConfig
from .persistent_store import PersistentStore

logger = logging.getLogger(__name__)


@dataclass
class InMemoryStore:
    """In-memory storage for OAuth data."""
    clients: Dict[str, OAuthClientInformationFull] = field(default_factory=dict)
    auth_codes: Dict[str, AuthorizationCode] = field(default_factory=dict)
    access_tokens: Dict[str, AccessToken] = field(default_factory=dict)
    refresh_tokens: Dict[str, RefreshToken] = field(default_factory=dict)
    
    def clear_expired_tokens(self):
        """Remove expired tokens from storage."""
        current_time = time.time()
        
        # Remove expired authorization codes
        expired_codes = [
            code for code, auth_code in self.auth_codes.items()
            if not code.startswith("pending_") and auth_code.expires_at < current_time
        ]
        for code in expired_codes:
            del self.auth_codes[code]
        
        # Remove expired access tokens
        expired_access = [
            token for token, access_token in self.access_tokens.items()
            if access_token.expires_at < current_time
        ]
        for token in expired_access:
            del self.access_tokens[token]
        
        # Remove expired refresh tokens
        expired_refresh = [
            token for token, refresh_token in self.refresh_tokens.items()
            if refresh_token.expires_at < current_time
        ]
        for token in expired_refresh:
            del self.refresh_tokens[token]


class InMemoryOAuthProvider(BaseOAuthProvider):
    """
    OAuth provider with persistent storage.
    
    Features:
    - Dynamic client registration (persisted)
    - Authorization code flow with PKCE
    - Token issuance and refresh
    - Token revocation
    - Persistent client registration and refresh tokens
    
    Client registrations and refresh tokens survive server restarts.
    """
    
    def __init__(self, config: ProviderConfig):
        """Initialize the provider with persistent storage."""
        super().__init__(config)
        self.store = PersistentStore()
        logger.info(f"OAuth provider initialized with persistent storage: {config.issuer_url}")
    
    async def initialize(self) -> None:
        """Initialize the provider (no-op for in-memory)."""
        logger.info("In-memory provider ready (no initialization needed)")
    
    def _generate_token(self, nbits: int = 256) -> str:
        """Generate a cryptographically secure random token."""
        return secrets.token_urlsafe(nbits // 8)
    
    async def get_client(self, client_id: str) -> Optional[OAuthClientInformationFull]:
        """Retrieve client information by ID."""
        return self.store.clients.get(client_id)
    
    async def register_client(
        self,
        client_info: OAuthClientInformationFull
    ) -> None:
        """Register a new OAuth client and persist to disk."""
        logger.info(f"=== CLIENT REGISTRATION ===")
        logger.info(f"Client ID: {client_info.client_id}")
        logger.info(f"Client Name: {client_info.client_name}")
        logger.info(f"Redirect URIs: {[str(uri) for uri in client_info.redirect_uris]}")
        logger.info(f"Grant Types: {client_info.grant_types if hasattr(client_info, 'grant_types') else 'Not specified'}")
        
        # The MCP library handles client ID/secret generation
        # We store and persist the client info
        self.store.register_client(client_info)
        logger.info(f"✅ Client registered and persisted successfully")
        logger.info(f"===========================")
    
    async def authorize(
        self,
        client: OAuthClientInformationFull,
        params: AuthorizationParams
    ) -> str:
        """Handle authorization request and return redirect URL for login/consent.
        
        Redirects to the internal login page to authenticate the user and request consent.
        """
        # Validate scopes
        scopes = self.validate_scopes(params.scopes)
        
        # Validate redirect URI
        redirect_uri = str(params.redirect_uri)
        if redirect_uri not in [str(uri) for uri in client.redirect_uris]:
            raise AuthorizeError(
                error="invalid_request",
                error_description="Invalid redirect_uri"
            )
        
        # Generate temporary key for the pending request
        temp_key = self._generate_token(32)
        expires_at = time.time() + 600  # 10 minutes to complete login/consent
        
        # Store pending authorization request
        # We prefix with "pending_" to distinguish from actual auth codes
        pending_key = f"pending_{temp_key}"
        
        auth_code = AuthorizationCode(
            code=temp_key,  # This is the temp key, not the final auth code
            scopes=scopes,
            expires_at=expires_at,
            client_id=client.client_id,
            code_challenge=params.code_challenge,
            redirect_uri=params.redirect_uri,
            redirect_uri_provided_explicitly=params.redirect_uri_provided_explicitly,
            resource=params.resource,
        )
        self.store.save_auth_code(pending_key, auth_code)
        
        # Store state separately (not in AuthorizationCode dataclass)
        # We'll retrieve it when completing authorization
        if params.state:
            self.store.save_auth_code(f"state_{temp_key}", AuthorizationCode(
                code=params.state,  # Store state in the code field
                scopes=[],
                expires_at=expires_at,
                client_id=client.client_id,
                code_challenge="",  # Required string field
                redirect_uri=params.redirect_uri,
                redirect_uri_provided_explicitly=False,
            ))
        
        logger.info(f"Initiating interactive authorization for client: {client.client_id}")
        logger.debug(f"Temp key: {temp_key}")
        
        # Construct redirect URL to our login page
        # We need to pass all parameters so they can be preserved through the login flow
        query_params = {
            "client_id": client.client_id,
            "redirect_uri": redirect_uri,
            "scope": " ".join(scopes),
            "state": params.state or "",
            "code_challenge": params.code_challenge or "",
            "temp_key": temp_key,
        }
        
        login_url = f"{self.config.issuer_url}/oauth/authorize/page?{urlencode(query_params)}"
        logger.info(f"Redirecting to login page: {login_url}")
        
        return login_url
    
    async def complete_authorization(
        self,
        temp_key: str,
        approved: bool = True
    ) -> Optional[str]:
        """Complete authorization after user consent."""
        pending_key = f"pending_{temp_key}"
        pending_request = self.store.auth_codes.get(pending_key)
        
        if not pending_request:
            logger.error(f"Pending authorization request not found: {temp_key[:8]}...")
            return None
        
        # Retrieve stored state
        state_key = f"state_{temp_key}"
        state_entry = self.store.auth_codes.get(state_key)
        stored_state = state_entry.code if state_entry else None
        
        # Remove pending request and state
        self.store.delete_auth_code(pending_key)
        if state_entry:
            self.store.delete_auth_code(state_key)
        
        if not approved:
            logger.info(f"Authorization denied for client: {pending_request.client_id}")
            redirect_url = construct_redirect_uri(
                str(pending_request.redirect_uri),
                error="access_denied",
                error_description="User denied authorization",
                state=stored_state,
            )
            return redirect_url
        
        # Generate actual authorization code
        code = self._generate_token(160)
        expires_at = int(time.time() + self.config.auth_code_ttl)
        
        auth_code = AuthorizationCode(
            code=code,
            scopes=pending_request.scopes,
            expires_at=expires_at,
            client_id=pending_request.client_id,
            code_challenge=pending_request.code_challenge,
            redirect_uri=pending_request.redirect_uri,
            redirect_uri_provided_explicitly=pending_request.redirect_uri_provided_explicitly,
            resource=pending_request.resource,
        )
        
        # Store authorization code
        self.store.save_auth_code(code, auth_code)
        logger.info(f"Authorization approved for client: {pending_request.client_id}")
        logger.info(f"Returning state to client: {stored_state[:20] if stored_state else 'None'}...")
        logger.debug(f"Code: {code[:8]}... (expires in {self.config.auth_code_ttl}s)")
        
        # Return redirect URI with code and state
        redirect_url = construct_redirect_uri(
            str(pending_request.redirect_uri),
            code=code,
            state=stored_state,
        )
        
        return redirect_url
    
    async def load_authorization_code(
        self,
        client: OAuthClientInformationFull,
        authorization_code: str
    ) -> Optional[AuthorizationCode]:
        """Load an authorization code."""
        logger.info(f"Loading authorization code: {authorization_code[:16]}... for client: {client.client_id}")
        
        if authorization_code.startswith("pending_"):
            logger.error(f"Attempted to load pending authorization code: {authorization_code[:8]}...")
            return None
        
        auth_code = self.store.auth_codes.get(authorization_code)
        
        if not auth_code:
            logger.error(f"Authorization code not found: {authorization_code[:16]}...")
            logger.error(f"Available codes in store: {len(self.store.auth_codes)}")
            return None
        
        if auth_code.client_id != client.client_id:
            logger.error(f"Authorization code client mismatch: expected {auth_code.client_id}, got {client.client_id}")
            return None
        
        if auth_code.expires_at < time.time():
            logger.error(f"Authorization code expired: {authorization_code[:16]}...")
            self.store.delete_auth_code(authorization_code)
            return None
        
        logger.info(f"Authorization code loaded successfully")
        return auth_code
    
    async def exchange_authorization_code(
        self,
        client: OAuthClientInformationFull,
        authorization_code: AuthorizationCode
    ) -> OAuthToken:
        """Exchange authorization code for tokens."""
        logger.info(f"Exchanging authorization code: {authorization_code.code[:16]}... for client: {client.client_id}")
        
        # Delete authorization code (one-time use)
        if authorization_code.code in self.store.auth_codes:
            self.store.delete_auth_code(authorization_code.code)
            logger.info(f"Deleted one-time authorization code")
        
        # Generate tokens
        access_token = self._generate_token(256)
        refresh_token = self._generate_token(256)
        
        access_expires_at = int(time.time() + self.config.access_token_ttl)
        refresh_expires_at = int(time.time() + self.config.refresh_token_ttl)
        
        # Store tokens
        access_token_obj = AccessToken(
            token=access_token,
            client_id=client.client_id,
            scopes=authorization_code.scopes,
            expires_at=access_expires_at,
            resource=authorization_code.resource,
        )
        self.store.add_access_token(access_token_obj)
        
        # Store and persist refresh token
        refresh_token_obj = RefreshToken(
            token=refresh_token,
            client_id=client.client_id,
            scopes=authorization_code.scopes,
            expires_at=refresh_expires_at,
        )
        self.store.add_refresh_token(refresh_token_obj)
        
        logger.info(f"Successfully exchanged code for tokens (client: {client.client_id})")
        logger.info(f"Access token expires in {self.config.access_token_ttl}s, refresh token expires in {self.config.refresh_token_ttl}s")
        
        # Return OAuthToken (standard OAuth 2.0 token response)
        return OAuthToken(
            access_token=access_token,
            token_type="Bearer",
            expires_in=self.config.access_token_ttl,
            refresh_token=refresh_token,
            scope=" ".join(authorization_code.scopes),
        )
    
    async def load_refresh_token(
        self,
        client: OAuthClientInformationFull,
        refresh_token: str
    ) -> Optional[RefreshToken]:
        """Load a refresh token."""
        token = self.store.refresh_tokens.get(refresh_token)
        
        if not token:
            return None
        
        if token.client_id != client.client_id:
            logger.warning(f"Refresh token client mismatch: {refresh_token[:8]}...")
            return None
        
        if token.expires_at < time.time():
            logger.debug(f"Refresh token expired: {refresh_token[:8]}...")
            self.store.remove_refresh_token(refresh_token)
            return None
        
        return token
    
    async def exchange_refresh_token(
        self,
        client: OAuthClientInformationFull,
        refresh_token: RefreshToken,
        requested_scopes: Optional[List[str]] = None
    ) -> OAuthToken:
        """Exchange refresh token for new tokens."""
        # Validate requested scopes don't exceed original grant
        if requested_scopes:
            granted_scopes = [s for s in requested_scopes if s in refresh_token.scopes]
        else:
            granted_scopes = refresh_token.scopes
        
        # Generate new tokens
        new_access_token = self._generate_token(256)
        new_refresh_token = self._generate_token(256)
        
        access_expires_at = int(time.time() + self.config.access_token_ttl)
        refresh_expires_at = int(time.time() + self.config.refresh_token_ttl)
        
        # Store new tokens
        access_token_obj = AccessToken(
            token=new_access_token,
            client_id=client.client_id,
            scopes=granted_scopes,
            expires_at=access_expires_at,
        )
        self.store.add_access_token(access_token_obj)
        
        # Store and persist new refresh token
        new_refresh_token_obj = RefreshToken(
            token=new_refresh_token,
            client_id=client.client_id,
            scopes=granted_scopes,
            expires_at=refresh_expires_at,
        )
        self.store.add_refresh_token(new_refresh_token_obj)
        
        # Revoke old refresh token (token rotation)
        if refresh_token.token in self.store.refresh_tokens:
            self.store.remove_refresh_token(refresh_token.token)
        
        logger.info(f"Refreshed tokens for client: {client.client_id}")
        
        # Return OAuthToken (standard OAuth 2.0 token response)
        return OAuthToken(
            access_token=new_access_token,
            token_type="Bearer",
            expires_in=self.config.access_token_ttl,
            refresh_token=new_refresh_token,
            scope=" ".join(granted_scopes),
        )
    
    async def load_access_token(
        self,
        token: str
    ) -> Optional[AccessToken]:
        """Load and validate an access token."""
        access_token = self.store.access_tokens.get(token)
        
        if not access_token:
            return None
        
        if access_token.expires_at < time.time():
            logger.debug(f"Access token expired: {token[:8]}...")
            self.store.remove_access_token(token)
            return None
        
        logger.debug(f"Access token valid: {token[:8]}... (client: {access_token.client_id})")
        return access_token
    
    async def revoke_token(
        self,
        client: OAuthClientInformationFull,
        token: str,
        token_type_hint: Optional[str] = None
    ) -> None:
        """Revoke an access or refresh token."""
        # Try to find and revoke the token
        if token in self.store.access_tokens:
            token_obj = self.store.access_tokens[token]
            if token_obj.client_id == client.client_id:
                self.store.remove_access_token(token)
                logger.info(f"Revoked access token: {token[:8]}...")
                return
        
        if token in self.store.refresh_tokens:
            token_obj = self.store.refresh_tokens[token]
            if token_obj.client_id == client.client_id:
                # Also revoke associated access tokens
                client_id = token_obj.client_id
                associated_access_tokens = [
                    t for t, at in self.store.access_tokens.items()
                    if at.client_id == client_id
                ]
                for access_token in associated_access_tokens:
                    self.store.remove_access_token(access_token)
                    logger.debug(f"Revoked associated access token: {access_token[:8]}...")
                
                self.store.remove_refresh_token(token)
                logger.info(f"Revoked refresh token: {token[:8]}...")
                return
    
    def get_stats(self) -> dict:
        """Get storage statistics (for debugging/monitoring)."""
        self.store.clear_expired_tokens()
        
        pending_count = sum(1 for key in self.store.auth_codes.keys() if key.startswith("pending_"))
        completed_codes = len(self.store.auth_codes) - pending_count
        
        base_stats = super().get_stats()
        return {
            **base_stats,
            "clients": len(self.store.clients),
            "pending_authorizations": pending_count,
            "authorization_codes": completed_codes,
            "access_tokens": len(self.store.access_tokens),
            "refresh_tokens": len(self.store.refresh_tokens),
        }
