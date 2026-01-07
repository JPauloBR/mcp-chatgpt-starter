"""
Azure Entra ID OAuth Provider

Integrates with Microsoft Azure Entra ID (formerly Azure AD) for authentication.
Uses Microsoft Identity Platform as the identity provider while MCP server
acts as the authorization server for tool access.
"""

import logging
import httpx
from typing import Optional, List
from urllib.parse import urlencode

from mcp.shared.auth import OAuthClientInformationFull, OAuthToken
from mcp.server.auth.provider import (
    AuthorizationParams,
    AuthorizationCode,
    RefreshToken,
    AccessToken,
    AuthorizeError,
)

from .base import BaseOAuthProvider, ProviderConfig
from .persistent_store import PersistentStore

logger = logging.getLogger(__name__)


class AzureEntraIDProvider(BaseOAuthProvider):
    """
    Azure Entra ID (Microsoft Identity Platform) OAuth provider with persistent storage.
    
    This provider delegates authentication to Azure Entra ID, then issues
    its own tokens for MCP tool access based on the Azure authentication.
    
    Features:
    - Azure AD / Entra ID authentication
    - Multi-tenant or single-tenant support
    - User profile from Microsoft Graph
    - Custom MCP token issuance
    - Scope mapping (Azure scopes → MCP scopes)
    - Persistent client registration and refresh tokens
    
    Setup:
    1. Register an application in Azure Portal
    2. Configure redirect URIs
    3. Add Microsoft Graph API permissions
    4. Set AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, and AZURE_TENANT_ID env vars
    
    Tenant Options:
    - Specific tenant: Use tenant ID
    - Multi-tenant: Use "organizations" or "common"
    - Consumer accounts: Use "consumers"
    """
    
    def __init__(self, config: ProviderConfig):
        """Initialize Azure Entra ID OAuth provider."""
        super().__init__(config)
        
        if not config.client_id or not config.client_secret:
            raise ValueError("Azure provider requires client_id and client_secret")
        
        # Default to "common" for multi-tenant if not specified
        self.tenant_id = config.tenant_id or "common"
        
        # Build Azure endpoints based on tenant
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.auth_endpoint = f"{self.authority}/oauth2/v2.0/authorize"
        self.token_endpoint = f"{self.authority}/oauth2/v2.0/token"
        self.userinfo_endpoint = "https://graph.microsoft.com/v1.0/me"
        
        self.store = PersistentStore()
        
        logger.info(f"Azure Entra ID provider initialized with persistent storage: tenant={self.tenant_id}")
    
    async def initialize(self) -> None:
        """Initialize provider (Azure doesn't require discovery)."""
        logger.info(f"Azure provider ready (authority: {self.authority})")
    
    async def get_client(self, client_id: str) -> Optional[OAuthClientInformationFull]:
        """Retrieve client information by ID."""
        return self.store.clients.get(client_id)
    
    async def register_client(
        self,
        client_info: OAuthClientInformationFull
    ) -> None:
        """Register a new OAuth client and persist to disk."""
        self.store.register_client(client_info)
        logger.info(f"Registered and persisted client: {client_info.client_id}")
    
    async def authorize(
        self,
        client: OAuthClientInformationFull,
        params: AuthorizationParams
    ) -> str:
        """
        Handle authorization request.
        
        Redirects to Azure Entra ID for user authentication, then shows
        consent page for MCP tool access.
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
        
        # Store authorization request temporarily
        import secrets
        temp_key = secrets.token_urlsafe(32)
        
        import time
        pending_auth = AuthorizationCode(
            code=temp_key,
            scopes=scopes,
            expires_at=time.time() + 600,
            client_id=client.client_id,
            code_challenge=params.code_challenge,
            redirect_uri=params.redirect_uri,
            redirect_uri_provided_explicitly=params.redirect_uri_provided_explicitly,
            resource=params.resource,
        )
        # Store the original state from ChatGPT to return later
        setattr(pending_auth, "_original_state", params.state)
        self.store.auth_codes[f"pending_{temp_key}"] = pending_auth
        
        logger.info(f"Azure OAuth authorization initiated for client: {client.client_id}")
        
        # Build Azure OAuth URL
        # Microsoft Graph scopes for basic profile
        azure_scopes = [
            "openid",
            "email",
            "profile",
            "User.Read",  # Microsoft Graph permission
        ]
        
        azure_params = {
            "client_id": self.config.client_id,
            "redirect_uri": f"{self.issuer_url}/oauth/azure/callback",
            "response_type": "code",
            "scope": " ".join(azure_scopes),
            "state": temp_key,  # Pass temp_key as state
            "response_mode": "query",
            "prompt": "consent",  # Force consent screen
        }
        
        azure_auth_url = f"{self.auth_endpoint}?{urlencode(azure_params)}"
        logger.debug(f"Redirecting to Azure OAuth: {azure_auth_url}")
        
        return azure_auth_url
    
    async def handle_azure_callback(
        self,
        code: str,
        state: str
    ) -> dict:
        """
        Handle callback from Azure OAuth.
        
        Exchanges Azure auth code for tokens and fetches user info.
        
        Returns:
            dict with user info and temp_key for completing MCP authorization
        """
        # Exchange code for Azure tokens
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                self.token_endpoint,
                data={
                    "code": code,
                    "client_id": self.config.client_id,
                    "client_secret": self.config.client_secret,
                    "redirect_uri": f"{self.issuer_url}/oauth/azure/callback",
                    "grant_type": "authorization_code",
                    "scope": "User.Read",
                }
            )
            token_response.raise_for_status()
            azure_tokens = token_response.json()
        
        # Fetch user info from Microsoft Graph
        async with httpx.AsyncClient() as client:
            userinfo_response = await client.get(
                self.userinfo_endpoint,
                headers={"Authorization": f"Bearer {azure_tokens['access_token']}"}
            )
            userinfo_response.raise_for_status()
            user_info = userinfo_response.json()
        
        logger.info(f"Azure authentication successful for user: {user_info.get('userPrincipalName')}")
        
        return {
            "user_info": user_info,
            "temp_key": state,  # State contains our temp_key
            "azure_tokens": azure_tokens,
        }
    
    async def complete_authorization(
        self,
        temp_key: str,
        approved: bool = True,
        user_info: Optional[dict] = None
    ) -> Optional[str]:
        """Complete authorization after user consent."""
        from mcp.server.auth.provider import construct_redirect_uri
        
        pending_key = f"pending_{temp_key}"
        pending_request = self.store.auth_codes.get(pending_key)
        
        if not pending_request:
            logger.error(f"Pending authorization request not found: {temp_key[:8]}...")
            return None
        
        del self.store.auth_codes[pending_key]
        
        if not approved:
            logger.info(f"Authorization denied for client: {pending_request.client_id}")
            return construct_redirect_uri(
                str(pending_request.redirect_uri),
                error="access_denied",
                error_description="User denied authorization",
            )
        
        # Generate MCP authorization code
        import secrets
        import time
        
        code = secrets.token_urlsafe(40)
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
        
        # Store authorization code with user info
        self.store.auth_codes[code] = auth_code
        
        if user_info:
            setattr(auth_code, "_user_info", user_info)
        
        # Get the original state from ChatGPT's request
        original_state = getattr(pending_request, "_original_state", None)
        
        logger.info(f"Azure authorization approved for client: {pending_request.client_id}")
        
        return construct_redirect_uri(
            str(pending_request.redirect_uri),
            code=code,
            state=original_state,
        )
    
    async def load_authorization_code(
        self,
        client: OAuthClientInformationFull,
        authorization_code: str
    ) -> Optional[AuthorizationCode]:
        """Load an authorization code."""
        if authorization_code.startswith("pending_"):
            return None
        
        auth_code = self.store.auth_codes.get(authorization_code)
        
        if not auth_code:
            return None
        
        if auth_code.client_id != client.client_id:
            return None
        
        import time
        if auth_code.expires_at < time.time():
            del self.store.auth_codes[authorization_code]
            return None
        
        return auth_code
    
    async def exchange_authorization_code(
        self,
        client: OAuthClientInformationFull,
        authorization_code: AuthorizationCode
    ) -> OAuthToken:
        """Exchange authorization code for MCP tokens."""
        if authorization_code.code in self.store.auth_codes:
            del self.store.auth_codes[authorization_code.code]
        
        import secrets
        import time
        
        access_token = secrets.token_urlsafe(64)
        refresh_token = secrets.token_urlsafe(64)
        
        access_expires_at = int(time.time() + self.config.access_token_ttl)
        refresh_expires_at = int(time.time() + self.config.refresh_token_ttl)
        
        self.store.access_tokens[access_token] = AccessToken(
            token=access_token,
            client_id=client.client_id,
            scopes=authorization_code.scopes,
            expires_at=access_expires_at,
            resource=authorization_code.resource,
        )
        
        # Store and persist refresh token
        refresh_token_obj = RefreshToken(
            token=refresh_token,
            client_id=client.client_id,
            scopes=authorization_code.scopes,
            expires_at=refresh_expires_at,
        )
        self.store.add_refresh_token(refresh_token_obj)
        
        logger.info(f"Issued MCP tokens for Azure-authenticated user (client: {client.client_id})")
        
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
            return None
        
        import time
        if token.expires_at < time.time():
            self.store.remove_refresh_token(refresh_token)
            return None
        
        return token
    
    async def exchange_refresh_token(
        self,
        client: OAuthClientInformationFull,
        refresh_token: RefreshToken,
        requested_scopes: Optional[List[str]] = None
    ) -> tuple[AccessToken, Optional[RefreshToken]]:
        """Exchange refresh token for new MCP tokens."""
        if requested_scopes:
            granted_scopes = [s for s in requested_scopes if s in refresh_token.scopes]
        else:
            granted_scopes = refresh_token.scopes
        
        import secrets
        import time
        
        new_access_token = secrets.token_urlsafe(64)
        new_refresh_token = secrets.token_urlsafe(64)
        
        access_expires_at = time.time() + self.config.access_token_ttl
        refresh_expires_at = time.time() + self.config.refresh_token_ttl
        
        self.store.access_tokens[new_access_token] = AccessToken(
            token=new_access_token,
            client_id=client.client_id,
            scopes=granted_scopes,
            expires_at=access_expires_at,
        )
        
        # Store and persist new refresh token
        new_refresh_token_obj = RefreshToken(
            token=new_refresh_token,
            client_id=client.client_id,
            scopes=granted_scopes,
            expires_at=refresh_expires_at,
        )
        self.store.add_refresh_token(new_refresh_token_obj)
        
        if refresh_token.token in self.store.refresh_tokens:
            self.store.remove_refresh_token(refresh_token.token)
        
        logger.info(f"Refreshed MCP tokens for client: {client.client_id}")
        
        return (
            self.store.access_tokens[new_access_token],
            new_refresh_token_obj
        )
    
    async def load_access_token(
        self,
        token: str
    ) -> Optional[AccessToken]:
        """Load and validate an MCP access token."""
        access_token = self.store.access_tokens.get(token)
        
        if not access_token:
            return None
        
        import time
        if access_token.expires_at < time.time():
            del self.store.access_tokens[token]
            return None
        
        return access_token
    
    async def revoke_token(
        self,
        client: OAuthClientInformationFull,
        token: str,
        token_type_hint: Optional[str] = None
    ) -> None:
        """Revoke an MCP access or refresh token."""
        if token in self.store.access_tokens:
            token_obj = self.store.access_tokens[token]
            if token_obj.client_id == client.client_id:
                del self.store.access_tokens[token]
                logger.info(f"Revoked access token")
                return
        
        if token in self.store.refresh_tokens:
            token_obj = self.store.refresh_tokens[token]
            if token_obj.client_id == client.client_id:
                client_id = token_obj.client_id
                associated_access_tokens = [
                    t for t, at in self.store.access_tokens.items()
                    if at.client_id == client_id
                ]
                for access_token in associated_access_tokens:
                    del self.store.access_tokens[access_token]
                
                self.store.remove_refresh_token(token)
                logger.info(f"Revoked refresh token")
                return
    
    def get_stats(self) -> dict:
        """Get provider statistics."""
        self.store.clear_expired_tokens()
        
        pending_count = sum(1 for key in self.store.auth_codes.keys() if key.startswith("pending_"))
        completed_codes = len(self.store.auth_codes) - pending_count
        
        base_stats = super().get_stats()
        return {
            **base_stats,
            "tenant_id": self.tenant_id,
            "clients": len(self.store.clients),
            "pending_authorizations": pending_count,
            "authorization_codes": completed_codes,
            "access_tokens": len(self.store.access_tokens),
            "refresh_tokens": len(self.store.refresh_tokens),
        }
