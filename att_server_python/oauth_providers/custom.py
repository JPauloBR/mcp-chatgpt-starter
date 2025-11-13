"""
Custom In-Memory OAuth Provider

Simple demo OAuth provider for testing and development.
Stores all tokens in memory (lost on restart).
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
    In-memory OAuth provider for demo/testing.
    
    Features:
    - Dynamic client registration
    - Authorization code flow with PKCE
    - Token issuance and refresh
    - Token revocation
    - In-memory storage (no persistence)
    
    Perfect for development and testing, not for production.
    """
    
    def __init__(self, config: ProviderConfig):
        """Initialize the in-memory provider."""
        super().__init__(config)
        self.store = InMemoryStore()
        logger.info(f"In-memory OAuth provider initialized: {config.issuer_url}")
    
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
        """Register a new OAuth client dynamically."""
        # The MCP library handles client ID/secret generation
        # We just store the client info as provided
        self.store.clients[client_info.client_id] = client_info
        logger.info(f"Registered client: {client_info.client_id}")
        logger.debug(f"Client redirect URIs: {client_info.redirect_uris}")
    
    async def authorize(
        self,
        client: OAuthClientInformationFull,
        params: AuthorizationParams
    ) -> str:
        """Handle authorization request and return redirect URL."""
        # Validate scopes
        scopes = self.validate_scopes(params.scopes)
        
        # Validate redirect URI
        redirect_uri = str(params.redirect_uri)
        if redirect_uri not in [str(uri) for uri in client.redirect_uris]:
            raise AuthorizeError(
                error="invalid_request",
                error_description="Invalid redirect_uri"
            )
        
        # Store authorization request temporarily (to be completed after user consent)
        temp_key = self._generate_token(128)
        self.store.auth_codes[f"pending_{temp_key}"] = AuthorizationCode(
            code=temp_key,
            scopes=scopes,
            expires_at=time.time() + 600,  # 10 minutes to complete authorization
            client_id=client.client_id,
            code_challenge=params.code_challenge,
            redirect_uri=params.redirect_uri,
            redirect_uri_provided_explicitly=params.redirect_uri_provided_explicitly,
            resource=params.resource,
        )
        
        logger.info(f"Authorization request initiated for client: {client.client_id}")
        
        # Redirect to consent page with all necessary parameters
        consent_params = {
            "client_id": client.client_id,
            "redirect_uri": redirect_uri,
            "state": params.state or "",
            "scope": " ".join(scopes),
            "code_challenge": params.code_challenge,
            "temp_key": temp_key,
            "provider": "custom",
        }
        
        consent_url = f"{self.issuer_url}/oauth/authorize/page?{urlencode(consent_params)}"
        logger.debug(f"Redirecting to consent page: {consent_url}")
        
        return consent_url
    
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
        
        # Remove pending request
        del self.store.auth_codes[pending_key]
        
        if not approved:
            logger.info(f"Authorization denied for client: {pending_request.client_id}")
            redirect_url = construct_redirect_uri(
                str(pending_request.redirect_uri),
                error="access_denied",
                error_description="User denied authorization",
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
        self.store.auth_codes[code] = auth_code
        logger.info(f"Authorization approved for client: {pending_request.client_id}")
        logger.debug(f"Code: {code[:8]}... (expires in {self.config.auth_code_ttl}s)")
        
        # Return redirect URI with code
        redirect_url = construct_redirect_uri(
            str(pending_request.redirect_uri),
            code=code,
            state=None,
        )
        
        return redirect_url
    
    async def load_authorization_code(
        self,
        client: OAuthClientInformationFull,
        authorization_code: str
    ) -> Optional[AuthorizationCode]:
        """Load an authorization code."""
        if authorization_code.startswith("pending_"):
            logger.debug(f"Attempted to load pending authorization code: {authorization_code[:8]}...")
            return None
        
        auth_code = self.store.auth_codes.get(authorization_code)
        
        if not auth_code:
            logger.debug(f"Authorization code not found: {authorization_code[:8]}...")
            return None
        
        if auth_code.client_id != client.client_id:
            logger.warning(f"Authorization code client mismatch: {authorization_code[:8]}...")
            return None
        
        if auth_code.expires_at < time.time():
            logger.debug(f"Authorization code expired: {authorization_code[:8]}...")
            del self.store.auth_codes[authorization_code]
            return None
        
        return auth_code
    
    async def exchange_authorization_code(
        self,
        client: OAuthClientInformationFull,
        authorization_code: AuthorizationCode
    ) -> OAuthToken:
        """Exchange authorization code for tokens."""
        # Delete authorization code (one-time use)
        if authorization_code.code in self.store.auth_codes:
            del self.store.auth_codes[authorization_code.code]
        
        # Generate tokens
        access_token = self._generate_token(256)
        refresh_token = self._generate_token(256)
        
        access_expires_at = int(time.time() + self.config.access_token_ttl)
        refresh_expires_at = int(time.time() + self.config.refresh_token_ttl)
        
        # Store tokens
        self.store.access_tokens[access_token] = AccessToken(
            token=access_token,
            client_id=client.client_id,
            scopes=authorization_code.scopes,
            expires_at=access_expires_at,
            resource=authorization_code.resource,
        )
        
        self.store.refresh_tokens[refresh_token] = RefreshToken(
            token=refresh_token,
            client_id=client.client_id,
            scopes=authorization_code.scopes,
            expires_at=refresh_expires_at,
        )
        
        logger.info(f"Exchanged authorization code for tokens (client: {client.client_id})")
        
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
            del self.store.refresh_tokens[refresh_token]
            return None
        
        return token
    
    async def exchange_refresh_token(
        self,
        client: OAuthClientInformationFull,
        refresh_token: RefreshToken,
        requested_scopes: Optional[List[str]] = None
    ) -> tuple[AccessToken, Optional[RefreshToken]]:
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
        self.store.access_tokens[new_access_token] = AccessToken(
            token=new_access_token,
            client_id=client.client_id,
            scopes=granted_scopes,
            expires_at=access_expires_at,
        )
        
        self.store.refresh_tokens[new_refresh_token] = RefreshToken(
            token=new_refresh_token,
            client_id=client.client_id,
            scopes=granted_scopes,
            expires_at=refresh_expires_at,
        )
        
        # Revoke old refresh token (token rotation)
        if refresh_token.token in self.store.refresh_tokens:
            del self.store.refresh_tokens[refresh_token.token]
        
        logger.info(f"Refreshed tokens for client: {client.client_id}")
        
        return (
            self.store.access_tokens[new_access_token],
            self.store.refresh_tokens[new_refresh_token]
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
            del self.store.access_tokens[token]
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
                del self.store.access_tokens[token]
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
                    del self.store.access_tokens[access_token]
                    logger.debug(f"Revoked associated access token: {access_token[:8]}...")
                
                del self.store.refresh_tokens[token]
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
