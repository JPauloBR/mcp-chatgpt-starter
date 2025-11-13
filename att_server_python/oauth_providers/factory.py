"""
OAuth Provider Factory

Creates OAuth provider instances based on configuration.
"""

import logging
from typing import Optional, Dict, List

from .base import BaseOAuthProvider, ProviderConfig
from .custom import InMemoryOAuthProvider
from .google import GoogleOAuthProvider
from .azure import AzureEntraIDProvider

logger = logging.getLogger(__name__)


# Registry of available providers
PROVIDER_REGISTRY: Dict[str, type[BaseOAuthProvider]] = {
    "custom": InMemoryOAuthProvider,
    "google": GoogleOAuthProvider,
    "azure": AzureEntraIDProvider,
}


def get_available_providers() -> List[str]:
    """Get list of available provider types."""
    return list(PROVIDER_REGISTRY.keys())


def create_oauth_provider(
    provider_type: str,
    config: ProviderConfig
) -> BaseOAuthProvider:
    """
    Create an OAuth provider instance.
    
    Args:
        provider_type: Type of provider ("custom", "google", "azure")
        config: Provider configuration
        
    Returns:
        Initialized OAuth provider instance
        
    Raises:
        ValueError: If provider type is not supported
    """
    if provider_type not in PROVIDER_REGISTRY:
        available = ", ".join(PROVIDER_REGISTRY.keys())
        raise ValueError(
            f"Unknown provider type: {provider_type}. "
            f"Available providers: {available}"
        )
    
    provider_class = PROVIDER_REGISTRY[provider_type]
    
    try:
        provider = provider_class(config)
        logger.info(f"Created {provider_type} OAuth provider: {config.provider_name}")
        return provider
    except Exception as e:
        logger.error(f"Failed to create {provider_type} provider: {e}")
        raise


def create_provider_from_env(
    provider_type: str,
    issuer_url: str,
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
    tenant_id: Optional[str] = None,
    valid_scopes: Optional[List[str]] = None,
    default_scopes: Optional[List[str]] = None,
    access_token_ttl: int = 3600,
    refresh_token_ttl: int = 86400,
    auth_code_ttl: int = 600,
) -> BaseOAuthProvider:
    """
    Create an OAuth provider from environment variables.
    
    Convenience function for creating providers with common configuration.
    
    Args:
        provider_type: Type of provider ("custom", "google", "azure")
        issuer_url: OAuth issuer URL (MCP server URL)
        client_id: OAuth client ID (required for google/azure)
        client_secret: OAuth client secret (required for google/azure)
        tenant_id: Azure tenant ID (optional, defaults to "common")
        valid_scopes: List of valid scopes
        default_scopes: List of default scopes
        access_token_ttl: Access token lifetime in seconds
        refresh_token_ttl: Refresh token lifetime in seconds
        auth_code_ttl: Authorization code lifetime in seconds
        
    Returns:
        Initialized OAuth provider instance
    """
    # Provider display names
    provider_names = {
        "custom": "Custom OAuth (In-Memory)",
        "google": "Google OAuth",
        "azure": "Azure Entra ID",
    }
    
    # Build configuration
    config = ProviderConfig(
        provider_type=provider_type,
        provider_name=provider_names.get(provider_type, provider_type),
        issuer_url=issuer_url,
        client_id=client_id,
        client_secret=client_secret,
        tenant_id=tenant_id,
        valid_scopes=valid_scopes or ["read", "write", "payment", "account"],
        default_scopes=default_scopes or ["read"],
        access_token_ttl=access_token_ttl,
        refresh_token_ttl=refresh_token_ttl,
        auth_code_ttl=auth_code_ttl,
    )
    
    return create_oauth_provider(provider_type, config)


def validate_provider_config(
    provider_type: str,
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
) -> tuple[bool, Optional[str]]:
    """
    Validate provider configuration.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if provider_type not in PROVIDER_REGISTRY:
        available = ", ".join(PROVIDER_REGISTRY.keys())
        return False, f"Unknown provider: {provider_type}. Available: {available}"
    
    # Custom provider doesn't need external credentials
    if provider_type == "custom":
        return True, None
    
    # Google and Azure require client credentials
    if provider_type in ["google", "azure"]:
        if not client_id:
            return False, f"{provider_type} provider requires OAUTH_CLIENT_ID"
        if not client_secret:
            return False, f"{provider_type} provider requires OAUTH_CLIENT_SECRET"
    
    return True, None
