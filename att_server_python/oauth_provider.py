"""In-memory OAuth provider for AT&T MCP Server.

This is a simple demo OAuth provider that stores tokens in memory.
It supports dynamic client registration and provides basic authorization/token flows.
For production, consider using persistent storage or external OAuth providers.
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field
from typing import Dict

from mcp.server.auth.provider import (
    AccessToken,
    AuthorizationCode,
    AuthorizationParams,
    AuthorizeError,
    OAuthAuthorizationServerProvider,
    RefreshToken,
    RegistrationError,
    TokenError,
    construct_redirect_uri,
)
from mcp.shared.auth import OAuthClientInformationFull, OAuthToken
from pydantic import AnyUrl

import logging

logger = logging.getLogger(__name__)


@dataclass
class InMemoryStore:
    """In-memory storage for OAuth entities."""
    
    # Client registration
    clients: Dict[str, OAuthClientInformationFull] = field(default_factory=dict)
    
    # Authorization codes (code -> AuthorizationCode)
    auth_codes: Dict[str, AuthorizationCode] = field(default_factory=dict)
    
    # Access tokens (token -> AccessToken)
    access_tokens: Dict[str, AccessToken] = field(default_factory=dict)
    
    # Refresh tokens (token -> RefreshToken)
    refresh_tokens: Dict[str, RefreshToken] = field(default_factory=dict)
    
    def clear_expired_tokens(self) -> None:
        """Remove expired tokens from storage."""
        current_time = time.time()
        
        # Clear expired authorization codes
        expired_codes = [
            code for code, auth_code in self.auth_codes.items()
            if auth_code.expires_at < current_time
        ]
        for code in expired_codes:
            del self.auth_codes[code]
            logger.debug(f"Cleared expired authorization code: {code[:8]}...")
        
        # Clear expired access tokens
        expired_access = [
            token for token, access_token in self.access_tokens.items()
            if access_token.expires_at and access_token.expires_at < current_time
        ]
        for token in expired_access:
            del self.access_tokens[token]
            logger.debug(f"Cleared expired access token: {token[:8]}...")
        
        # Clear expired refresh tokens
        expired_refresh = [
            token for token, refresh_token in self.refresh_tokens.items()
            if refresh_token.expires_at and refresh_token.expires_at < current_time
        ]
        for token in expired_refresh:
            del self.refresh_tokens[token]
            logger.debug(f"Cleared expired refresh token: {token[:8]}...")


class InMemoryOAuthProvider(OAuthAuthorizationServerProvider[AuthorizationCode, RefreshToken, AccessToken]):
    """Simple in-memory OAuth provider for demo/testing purposes."""
    
    def __init__(
        self,
        issuer_url: str,
        valid_scopes: list[str] | None = None,
        default_scopes: list[str] | None = None,
        access_token_ttl: int = 3600,  # 1 hour
        refresh_token_ttl: int = 86400,  # 24 hours
        auth_code_ttl: int = 600,  # 10 minutes
    ):
        """Initialize the OAuth provider.
        
        Args:
            issuer_url: The OAuth issuer URL (base URL of the MCP server)
            valid_scopes: List of valid scopes that can be requested
            default_scopes: Default scopes to grant if none specified
            access_token_ttl: Access token time-to-live in seconds
            refresh_token_ttl: Refresh token time-to-live in seconds
            auth_code_ttl: Authorization code time-to-live in seconds
        """
        self.issuer_url = issuer_url.rstrip("/")
        self.valid_scopes = valid_scopes or ["read", "write"]
        self.default_scopes = default_scopes or ["read"]
        self.access_token_ttl = access_token_ttl
        self.refresh_token_ttl = refresh_token_ttl
        self.auth_code_ttl = auth_code_ttl
        self.store = InMemoryStore()
        
        logger.info(f"OAuth provider initialized with issuer: {self.issuer_url}")
        logger.info(f"Valid scopes: {self.valid_scopes}")
        logger.info(f"Default scopes: {self.default_scopes}")
    
    def _generate_token(self, bits: int = 256) -> str:
        """Generate a secure random token."""
        return secrets.token_urlsafe(bits // 8)
    
    def _validate_scopes(self, requested_scopes: list[str] | None) -> list[str]:
        """Validate and return scopes."""
        if not requested_scopes:
            return self.default_scopes
        
        # Check all requested scopes are valid
        invalid_scopes = [s for s in requested_scopes if s not in self.valid_scopes]
        if invalid_scopes:
            raise ValueError(f"Invalid scopes requested: {invalid_scopes}")
        
        return requested_scopes
    
    async def get_client(self, client_id: str) -> OAuthClientInformationFull | None:
        """Get registered client information."""
        self.store.clear_expired_tokens()  # Cleanup on access
        client = self.store.clients.get(client_id)
        if client:
            logger.debug(f"Retrieved client: {client_id}")
        else:
            logger.debug(f"Client not found: {client_id}")
        return client
    
    async def register_client(self, client_info: OAuthClientInformationFull) -> None:
        """Register a new OAuth client (dynamic client registration)."""
        client_id = client_info.client_id
        
        # Validate redirect URIs
        if not client_info.redirect_uris:
            raise RegistrationError(
                error="invalid_redirect_uri",
                error_description="At least one redirect URI is required"
            )
        
        # Store client
        self.store.clients[client_id] = client_info
        logger.info(f"Registered client: {client_id}")
        logger.debug(f"Client redirect URIs: {client_info.redirect_uris}")
    
    async def authorize(
        self,
        client: OAuthClientInformationFull,
        params: AuthorizationParams
    ) -> str:
        """Handle authorization request and return redirect URL.
        
        This redirects to the consent page where the user can approve/deny.
        """
        # Validate scopes
        try:
            scopes = self._validate_scopes(params.scopes)
        except ValueError as e:
            raise AuthorizeError(
                error="invalid_scope",
                error_description=str(e)
            )
        
        # Validate redirect URI
        redirect_uri = str(params.redirect_uri)
        if redirect_uri not in [str(uri) for uri in client.redirect_uris]:
            raise AuthorizeError(
                error="invalid_request",
                error_description="Invalid redirect_uri"
            )
        
        # Store authorization request temporarily (to be completed after user consent)
        # We'll use a temporary key to look this up when user approves
        temp_key = self._generate_token(128)
        self.store.auth_codes[f"pending_{temp_key}"] = AuthorizationCode(
            code=temp_key,  # Temporary, will be replaced on approval
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
        from urllib.parse import urlencode
        consent_params = {
            "client_id": client.client_id,
            "redirect_uri": redirect_uri,
            "state": params.state or "",
            "scope": " ".join(scopes),
            "code_challenge": params.code_challenge,
            "temp_key": temp_key,  # To look up pending request
        }
        
        consent_url = f"{self.issuer_url}/oauth/authorize/page?{urlencode(consent_params)}"
        logger.debug(f"Redirecting to consent page: {consent_url}")
        
        return consent_url
    
    async def complete_authorization(
        self,
        temp_key: str,
        approved: bool = True
    ) -> str | None:
        """Complete authorization after user consent.
        
        Args:
            temp_key: Temporary key from the pending authorization request
            approved: Whether user approved the request
            
        Returns:
            Redirect URL with authorization code if approved, None if denied
        """
        pending_key = f"pending_{temp_key}"
        pending_request = self.store.auth_codes.get(pending_key)
        
        if not pending_request:
            logger.error(f"Pending authorization request not found: {temp_key[:8]}...")
            return None
        
        # Remove pending request
        del self.store.auth_codes[pending_key]
        
        if not approved:
            logger.info(f"Authorization denied for client: {pending_request.client_id}")
            # Redirect with error
            redirect_url = construct_redirect_uri(
                str(pending_request.redirect_uri),
                error="access_denied",
                error_description="User denied authorization",
            )
            return redirect_url
        
        # Generate actual authorization code
        code = self._generate_token(160)
        expires_at = time.time() + self.auth_code_ttl
        
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
        logger.debug(f"Code: {code[:8]}... (expires in {self.auth_code_ttl}s)")
        
        # Return redirect URI with code
        redirect_url = construct_redirect_uri(
            str(pending_request.redirect_uri),
            code=code,
            state=None,  # State is handled by the page
        )
        
        return redirect_url
    
    async def load_authorization_code(
        self,
        client: OAuthClientInformationFull,
        authorization_code: str
    ) -> AuthorizationCode | None:
        """Load an authorization code."""
        # Don't load pending authorization requests (not yet approved)
        if authorization_code.startswith("pending_"):
            logger.debug(f"Attempted to load pending authorization code: {authorization_code[:8]}...")
            return None
        
        auth_code = self.store.auth_codes.get(authorization_code)
        
        if not auth_code:
            logger.debug(f"Authorization code not found: {authorization_code[:8]}...")
            return None
        
        # Verify code belongs to this client
        if auth_code.client_id != client.client_id:
            logger.warning(f"Authorization code client mismatch: {authorization_code[:8]}...")
            return None
        
        # Check expiration
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
        """Exchange authorization code for access and refresh tokens."""
        # Generate tokens
        access_token = self._generate_token()
        refresh_token = self._generate_token()
        
        access_expires_at = int(time.time() + self.access_token_ttl)
        refresh_expires_at = int(time.time() + self.refresh_token_ttl)
        
        # Store access token
        self.store.access_tokens[access_token] = AccessToken(
            token=access_token,
            client_id=client.client_id,
            scopes=authorization_code.scopes,
            expires_at=access_expires_at,
            resource=authorization_code.resource,
        )
        
        # Store refresh token
        self.store.refresh_tokens[refresh_token] = RefreshToken(
            token=refresh_token,
            client_id=client.client_id,
            scopes=authorization_code.scopes,
            expires_at=refresh_expires_at,
        )
        
        # Delete used authorization code
        if authorization_code.code in self.store.auth_codes:
            del self.store.auth_codes[authorization_code.code]
        
        logger.info(f"Exchanged authorization code for tokens (client: {client.client_id})")
        logger.debug(f"Access token: {access_token[:8]}... (expires in {self.access_token_ttl}s)")
        logger.debug(f"Refresh token: {refresh_token[:8]}... (expires in {self.refresh_token_ttl}s)")
        
        return OAuthToken(
            access_token=access_token,
            token_type="Bearer",
            expires_in=self.access_token_ttl,
            refresh_token=refresh_token,
            scope=" ".join(authorization_code.scopes) if authorization_code.scopes else None,
        )
    
    async def load_refresh_token(
        self,
        client: OAuthClientInformationFull,
        refresh_token: str
    ) -> RefreshToken | None:
        """Load a refresh token."""
        token = self.store.refresh_tokens.get(refresh_token)
        
        if not token:
            logger.debug(f"Refresh token not found: {refresh_token[:8]}...")
            return None
        
        # Verify token belongs to this client
        if token.client_id != client.client_id:
            logger.warning(f"Refresh token client mismatch: {refresh_token[:8]}...")
            return None
        
        # Check expiration
        if token.expires_at and token.expires_at < time.time():
            logger.debug(f"Refresh token expired: {refresh_token[:8]}...")
            del self.store.refresh_tokens[refresh_token]
            return None
        
        return token
    
    async def exchange_refresh_token(
        self,
        client: OAuthClientInformationFull,
        refresh_token: RefreshToken,
        scopes: list[str],
    ) -> OAuthToken:
        """Exchange refresh token for new access and refresh tokens."""
        # Validate requested scopes don't exceed original grant
        if scopes:
            invalid_scopes = [s for s in scopes if s not in refresh_token.scopes]
            if invalid_scopes:
                raise TokenError(
                    error="invalid_scope",
                    error_description=f"Requested scopes exceed original grant: {invalid_scopes}"
                )
            granted_scopes = scopes
        else:
            granted_scopes = refresh_token.scopes
        
        # Generate new tokens
        new_access_token = self._generate_token()
        new_refresh_token = self._generate_token()
        
        access_expires_at = int(time.time() + self.access_token_ttl)
        refresh_expires_at = int(time.time() + self.refresh_token_ttl)
        
        # Store new access token
        self.store.access_tokens[new_access_token] = AccessToken(
            token=new_access_token,
            client_id=client.client_id,
            scopes=granted_scopes,
            expires_at=access_expires_at,
        )
        
        # Store new refresh token
        self.store.refresh_tokens[new_refresh_token] = RefreshToken(
            token=new_refresh_token,
            client_id=client.client_id,
            scopes=granted_scopes,
            expires_at=refresh_expires_at,
        )
        
        # Revoke old refresh token (token rotation)
        if refresh_token.token in self.store.refresh_tokens:
            del self.store.refresh_tokens[refresh_token.token]
        
        logger.info(f"Exchanged refresh token for new tokens (client: {client.client_id})")
        logger.debug(f"New access token: {new_access_token[:8]}...")
        logger.debug(f"New refresh token: {new_refresh_token[:8]}...")
        
        return OAuthToken(
            access_token=new_access_token,
            token_type="Bearer",
            expires_in=self.access_token_ttl,
            refresh_token=new_refresh_token,
            scope=" ".join(granted_scopes) if granted_scopes else None,
        )
    
    async def load_access_token(self, token: str) -> AccessToken | None:
        """Verify and load an access token."""
        access_token = self.store.access_tokens.get(token)
        
        if not access_token:
            logger.debug(f"Access token not found: {token[:8]}...")
            return None
        
        # Check expiration
        if access_token.expires_at and access_token.expires_at < time.time():
            logger.debug(f"Access token expired: {token[:8]}...")
            del self.store.access_tokens[token]
            return None
        
        logger.debug(f"Access token valid: {token[:8]}... (client: {access_token.client_id})")
        return access_token
    
    async def revoke_token(
        self,
        token: AccessToken | RefreshToken,
    ) -> None:
        """Revoke an access or refresh token."""
        # Revoke access token if provided
        if isinstance(token, AccessToken) and token.token in self.store.access_tokens:
            del self.store.access_tokens[token.token]
            logger.info(f"Revoked access token: {token.token[:8]}...")
        
        # Revoke refresh token if provided
        if isinstance(token, RefreshToken) and token.token in self.store.refresh_tokens:
            # Also revoke associated access tokens (find by client_id)
            client_id = token.client_id
            associated_access_tokens = [
                t for t, at in self.store.access_tokens.items()
                if at.client_id == client_id
            ]
            for access_token in associated_access_tokens:
                del self.store.access_tokens[access_token]
                logger.debug(f"Revoked associated access token: {access_token[:8]}...")
            
            del self.store.refresh_tokens[token.token]
            logger.info(f"Revoked refresh token: {token.token[:8]}...")
    
    def get_stats(self) -> dict:
        """Get storage statistics (for debugging/monitoring)."""
        self.store.clear_expired_tokens()
        
        # Separate pending authorization requests from completed codes
        pending_count = sum(1 for key in self.store.auth_codes.keys() if key.startswith("pending_"))
        completed_codes = len(self.store.auth_codes) - pending_count
        
        return {
            "clients": len(self.store.clients),
            "pending_authorizations": pending_count,
            "authorization_codes": completed_codes,
            "access_tokens": len(self.store.access_tokens),
            "refresh_tokens": len(self.store.refresh_tokens),
        }
