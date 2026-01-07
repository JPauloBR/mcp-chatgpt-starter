"""
Persistent OAuth Storage

JSON-based persistent storage for OAuth clients, tokens, and authorization codes.
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, Optional
from dataclasses import asdict
from threading import Lock

from mcp.shared.auth import OAuthClientInformationFull
from mcp.server.auth.provider import AuthorizationCode, AccessToken, RefreshToken

logger = logging.getLogger(__name__)


class PersistentStore:
    """
    Persistent storage for OAuth data using JSON files.
    
    Stores:
    - Client registrations (persisted)
    - Authorization codes (in-memory only, short-lived)
    - Access tokens (in-memory only, short-lived)
    - Refresh tokens (persisted for long-term sessions)
    """
    
    def __init__(self, storage_dir: str = ".oauth_data"):
        """
        Initialize persistent storage.
        
        Args:
            storage_dir: Directory to store OAuth data files
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        self.clients_file = self.storage_dir / "clients.json"
        self.refresh_tokens_file = self.storage_dir / "refresh_tokens.json"
        
        # In-memory stores (not persisted)
        self.auth_codes: Dict[str, AuthorizationCode] = {}
        self.access_tokens: Dict[str, AccessToken] = {}
        
        # Persistent stores (loaded from disk)
        self.clients: Dict[str, OAuthClientInformationFull] = {}
        self.refresh_tokens: Dict[str, RefreshToken] = {}
        
        # Thread safety
        self._lock = Lock()
        
        # Load persisted data
        self._load_clients()
        self._load_refresh_tokens()
        
        logger.info(f"Persistent storage initialized at {self.storage_dir}")
        logger.info(f"Loaded {len(self.clients)} clients and {len(self.refresh_tokens)} refresh tokens")
    
    def _load_clients(self):
        """Load client registrations from disk."""
        if not self.clients_file.exists():
            return
        
        try:
            with open(self.clients_file, 'r') as f:
                data = json.load(f)
            
            # Convert JSON back to OAuthClientInformationFull objects
            for client_id, client_data in data.items():
                try:
                    # OAuthClientInformationFull expects specific types
                    # Make a copy to avoid modifying the original
                    client_params = dict(client_data)
                    
                    # Remove client_secret_hash if it's None or not present
                    if 'client_secret_hash' in client_params and client_params['client_secret_hash'] is None:
                        del client_params['client_secret_hash']
                    
                    # Ensure grant_types is present
                    if 'grant_types' not in client_params:
                        client_params['grant_types'] = ['authorization_code', 'refresh_token']
                    
                    self.clients[client_id] = OAuthClientInformationFull(**client_params)
                    logger.debug(f"Loaded client {client_id}: {client_params.get('client_name', 'Unknown')}")
                except Exception as e:
                    logger.error(f"Failed to load client {client_id}: {e}", exc_info=True)
            
            logger.info(f"Loaded {len(self.clients)} clients from {self.clients_file}")
        except Exception as e:
            logger.error(f"Failed to load clients from disk: {e}", exc_info=True)
    
    def _save_clients(self):
        """Save client registrations to disk."""
        try:
            with self._lock:
                data = {}
                for client_id, client in self.clients.items():
                    # Convert to dict for JSON serialization
                    client_dict = {
                        "client_id": client.client_id,
                        "client_name": client.client_name,
                        "redirect_uris": [str(uri) for uri in client.redirect_uris],
                        "grant_types": list(client.grant_types) if hasattr(client, 'grant_types') else ["authorization_code", "refresh_token"],
                    }
                    
                    # Only include client_secret_hash if it exists and is not None
                    if hasattr(client, 'client_secret_hash') and client.client_secret_hash is not None:
                        client_dict["client_secret_hash"] = client.client_secret_hash
                    
                    data[client_id] = client_dict
                
                with open(self.clients_file, 'w') as f:
                    json.dump(data, f, indent=2)
                
                logger.debug(f"Saved {len(self.clients)} clients to {self.clients_file}")
        except Exception as e:
            logger.error(f"Failed to save clients to disk: {e}")
    
    def _load_refresh_tokens(self):
        """Load refresh tokens from disk."""
        if not self.refresh_tokens_file.exists():
            return
        
        try:
            with open(self.refresh_tokens_file, 'r') as f:
                data = json.load(f)
            
            current_time = time.time()
            loaded_count = 0
            expired_count = 0
            
            # Convert JSON back to RefreshToken objects
            for token_value, token_data in data.items():
                try:
                    # Skip expired tokens
                    if token_data["expires_at"] < current_time:
                        expired_count += 1
                        continue
                    
                    self.refresh_tokens[token_value] = RefreshToken(
                        token=token_data["token"],
                        client_id=token_data["client_id"],
                        scopes=token_data["scopes"],
                        expires_at=token_data["expires_at"],
                    )
                    loaded_count += 1
                except Exception as e:
                    logger.error(f"Failed to load refresh token: {e}")
            
            logger.info(f"Loaded {loaded_count} refresh tokens, skipped {expired_count} expired")
        except Exception as e:
            logger.error(f"Failed to load refresh tokens from disk: {e}")
    
    def _save_refresh_tokens(self):
        """Save refresh tokens to disk."""
        try:
            with self._lock:
                current_time = time.time()
                data = {}
                
                # Only save non-expired tokens
                for token_value, token in self.refresh_tokens.items():
                    if token.expires_at > current_time:
                        data[token_value] = {
                            "token": token.token,
                            "client_id": token.client_id,
                            "scopes": token.scopes,
                            "expires_at": token.expires_at,
                        }
                
                with open(self.refresh_tokens_file, 'w') as f:
                    json.dump(data, f, indent=2)
                
                logger.debug(f"Saved {len(data)} refresh tokens to {self.refresh_tokens_file}")
        except Exception as e:
            logger.error(f"Failed to save refresh tokens to disk: {e}")
    
    def register_client(self, client: OAuthClientInformationFull):
        """Register a new client and persist to disk."""
        with self._lock:
            self.clients[client.client_id] = client
        self._save_clients()
        logger.info(f"Registered and persisted client: {client.client_id}")
    
    def get_client(self, client_id: str) -> Optional[OAuthClientInformationFull]:
        """Get a client by ID."""
        return self.clients.get(client_id)
    
    def add_refresh_token(self, token: RefreshToken):
        """Add a refresh token and persist to disk."""
        with self._lock:
            self.refresh_tokens[token.token] = token
        self._save_refresh_tokens()
    
    def remove_refresh_token(self, token_value: str):
        """Remove a refresh token and update disk."""
        with self._lock:
            if token_value in self.refresh_tokens:
                del self.refresh_tokens[token_value]
        self._save_refresh_tokens()
    
    def clear_expired_tokens(self):
        """Remove expired tokens from memory and disk."""
        current_time = time.time()
        
        # Clear expired authorization codes (in-memory only)
        expired_codes = [
            code for code, auth_code in self.auth_codes.items()
            if not code.startswith("pending_") and auth_code.expires_at < current_time
        ]
        for code in expired_codes:
            del self.auth_codes[code]
        
        # Clear expired access tokens (in-memory only)
        expired_access = [
            token for token, access_token in self.access_tokens.items()
            if access_token.expires_at < current_time
        ]
        for token in expired_access:
            del self.access_tokens[token]
        
        # Clear expired refresh tokens (also updates disk)
        expired_refresh = [
            token for token, refresh_token in self.refresh_tokens.items()
            if refresh_token.expires_at < current_time
        ]
        if expired_refresh:
            with self._lock:
                for token in expired_refresh:
                    del self.refresh_tokens[token]
            self._save_refresh_tokens()
            logger.info(f"Cleared {len(expired_refresh)} expired refresh tokens")
