"""
Base OAuth Provider Interface

All OAuth providers must implement this interface to work with the MCP server.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List
from mcp.shared.auth import OAuthClientInformationFull
from mcp.server.auth.provider import (
    OAuthAuthorizationServerProvider,
    AuthorizationParams,
    AuthorizationCode,
    RefreshToken,
    AccessToken,
)


@dataclass
class ProviderConfig:
    """Configuration for an OAuth provider."""
    
    # Provider identification
    provider_type: str  # "custom", "google", "azure"
    provider_name: str  # Display name
    
    # OAuth endpoints
    issuer_url: str
    authorization_endpoint: Optional[str] = None
    token_endpoint: Optional[str] = None
    userinfo_endpoint: Optional[str] = None
    
    # Provider-specific settings
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    tenant_id: Optional[str] = None  # For Azure
    
    # Scopes
    valid_scopes: List[str] = None
    default_scopes: List[str] = None
    
    # Token TTLs (seconds)
    access_token_ttl: int = 3600  # 1 hour
    refresh_token_ttl: int = 86400  # 24 hours
    auth_code_ttl: int = 600  # 10 minutes
    
    # UI customization
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.valid_scopes is None:
            self.valid_scopes = ["read", "write", "payment", "account"]
        if self.default_scopes is None:
            self.default_scopes = ["read"]


class BaseOAuthProvider(OAuthAuthorizationServerProvider, ABC):
    """
    Base class for all OAuth providers.
    
    Providers must implement the OAuthAuthorizationServerProvider protocol
    and can optionally override methods for provider-specific behavior.
    """
    
    def __init__(self, config: ProviderConfig):
        """Initialize the provider with configuration."""
        self.config = config
        self.issuer_url = config.issuer_url
    
    @abstractmethod
    async def initialize(self) -> None:
        """
        Initialize the provider (fetch OIDC discovery, etc.).
        
        This is called after provider creation to allow async setup.
        """
        pass
    
    @abstractmethod
    async def complete_authorization(
        self,
        temp_key: str,
        approved: bool = True
    ) -> Optional[str]:
        """
        Complete authorization after user consent.
        
        This is called when the user clicks approve/deny on the consent page.
        
        Args:
            temp_key: Temporary key from the pending authorization request
            approved: Whether user approved the request
            
        Returns:
            Redirect URL with authorization code if approved, None if denied
        """
        pass
    
    def get_provider_info(self) -> dict:
        """Get provider information for UI display."""
        return {
            "type": self.config.provider_type,
            "name": self.config.provider_name,
            "issuer_url": self.config.issuer_url,
            "logo_url": self.config.logo_url,
            "primary_color": self.config.primary_color,
        }
    
    def get_stats(self) -> dict:
        """Get provider statistics (for monitoring)."""
        return {
            "provider_type": self.config.provider_type,
            "provider_name": self.config.provider_name,
        }
    
    def validate_scopes(self, requested_scopes: List[str]) -> List[str]:
        """Validate and filter requested scopes."""
        if not requested_scopes:
            return self.config.default_scopes
        
        # Filter to only valid scopes
        valid = [s for s in requested_scopes if s in self.config.valid_scopes]
        
        # Return default scopes if none are valid
        return valid if valid else self.config.default_scopes
