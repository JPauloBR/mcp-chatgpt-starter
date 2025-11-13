"""
OAuth Provider Abstraction Layer

Supports multiple OAuth providers:
- Custom in-memory provider (demo/testing)
- Google OAuth/OIDC
- Azure Entra ID (Microsoft Identity Platform)
"""

from .base import BaseOAuthProvider, ProviderConfig
from .custom import InMemoryOAuthProvider
from .factory import create_oauth_provider, get_available_providers

__all__ = [
    "BaseOAuthProvider",
    "ProviderConfig",
    "InMemoryOAuthProvider",
    "create_oauth_provider",
    "get_available_providers",
]
