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
    - Access tokens (persisted, short-lived but survive restarts)
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
        self.access_tokens_file = self.storage_dir / "access_tokens.json"
        self.auth_codes_file = self.storage_dir / "auth_codes.json"
        
        # In-memory stores (now persisted)
        self.auth_codes: Dict[str, AuthorizationCode] = {}
        
        # Persistent stores (loaded from disk)
        self.clients: Dict[str, OAuthClientInformationFull] = {}
        self.refresh_tokens: Dict[str, RefreshToken] = {}
        self.access_tokens: Dict[str, AccessToken] = {}
        
        # Thread safety
        self._lock = Lock()
        
        # Load persisted data
        self._load_clients()
        self._load_refresh_tokens()
        self._load_access_tokens()
        self._load_auth_codes()
        
        logger.info(f"Persistent storage initialized at {self.storage_dir}")
        logger.info(f"Loaded {len(self.clients)} clients, {len(self.refresh_tokens)} refresh tokens, {len(self.access_tokens)} access tokens, and {len(self.auth_codes)} auth codes")
    
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
                    
                    # Ensure scope is present - use default scopes if not set
                    # This is critical for authorization validation
                    if 'scope' not in client_params or client_params['scope'] is None:
                        client_params['scope'] = 'read write payment account'
                    
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
                    
                    # Save scope field (required for authorization validation)
                    if hasattr(client, 'scope') and client.scope is not None:
                        client_dict["scope"] = client.scope
                    
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
    
    def _load_access_tokens(self):
        """Load access tokens from disk."""
        if not self.access_tokens_file.exists():
            return
        
        try:
            with open(self.access_tokens_file, 'r') as f:
                data = json.load(f)
            
            current_time = time.time()
            loaded_count = 0
            expired_count = 0
            
            # Convert JSON back to AccessToken objects
            for token_value, token_data in data.items():
                try:
                    # Skip expired tokens
                    if token_data["expires_at"] < current_time:
                        expired_count += 1
                        continue
                    
                    self.access_tokens[token_value] = AccessToken(
                        token=token_data["token"],
                        client_id=token_data["client_id"],
                        scopes=token_data["scopes"],
                        expires_at=token_data["expires_at"],
                        resource=token_data.get("resource")
                    )
                    loaded_count += 1
                except Exception as e:
                    logger.error(f"Failed to load access token: {e}")
            
            logger.info(f"Loaded {loaded_count} access tokens, skipped {expired_count} expired")
        except Exception as e:
            logger.error(f"Failed to load access tokens from disk: {e}")

    def _save_access_tokens(self):
        """Save access tokens to disk."""
        try:
            with self._lock:
                current_time = time.time()
                data = {}
                
                # Only save non-expired tokens
                for token_value, token in self.access_tokens.items():
                    if token.expires_at > current_time:
                        token_dict = {
                            "token": token.token,
                            "client_id": token.client_id,
                            "scopes": token.scopes,
                            "expires_at": token.expires_at,
                        }
                        if hasattr(token, "resource") and token.resource:
                             token_dict["resource"] = token.resource
                        data[token_value] = token_dict
                
                with open(self.access_tokens_file, 'w') as f:
                    json.dump(data, f, indent=2)
                
                logger.debug(f"Saved {len(data)} access tokens to {self.access_tokens_file}")
        except Exception as e:
            logger.error(f"Failed to save access tokens to disk: {e}")

    def _load_auth_codes(self):
        """Load authorization codes from disk."""
        if not self.auth_codes_file.exists():
            return
        
        try:
            with open(self.auth_codes_file, 'r') as f:
                data = json.load(f)
            
            current_time = time.time()
            loaded_count = 0
            expired_count = 0
            
            for key, code_data in data.items():
                try:
                    # Skip expired codes
                    if code_data["expires_at"] < current_time:
                        expired_count += 1
                        continue
                    
                    self.auth_codes[key] = AuthorizationCode(
                        code=code_data["code"],
                        client_id=code_data["client_id"],
                        scopes=code_data["scopes"],
                        expires_at=code_data["expires_at"],
                        code_challenge=code_data.get("code_challenge"),
                        redirect_uri=code_data.get("redirect_uri"),
                        redirect_uri_provided_explicitly=code_data.get("redirect_uri_provided_explicitly", False),
                        resource=code_data.get("resource")
                    )
                    loaded_count += 1
                except Exception as e:
                    logger.error(f"Failed to load auth code: {e}")
            
            logger.info(f"Loaded {loaded_count} auth codes, skipped {expired_count} expired")
        except Exception as e:
            logger.error(f"Failed to load auth codes from disk: {e}")

    def _save_auth_codes(self):
        """Save authorization codes to disk."""
        try:
            with self._lock:
                current_time = time.time()
                data = {}
                
                for key, code in self.auth_codes.items():
                    # Only save non-expired codes
                    if code.expires_at > current_time:
                        code_dict = {
                            "code": code.code,
                            "client_id": code.client_id,
                            "scopes": code.scopes,
                            "expires_at": code.expires_at,
                            "code_challenge": code.code_challenge,
                            "redirect_uri": str(code.redirect_uri) if code.redirect_uri else None,
                            "redirect_uri_provided_explicitly": code.redirect_uri_provided_explicitly,
                        }
                        if hasattr(code, "resource") and code.resource:
                             code_dict["resource"] = code.resource
                        data[key] = code_dict
                
                with open(self.auth_codes_file, 'w') as f:
                    json.dump(data, f, indent=2)
                
                logger.debug(f"Saved {len(data)} auth codes to {self.auth_codes_file}")
        except Exception as e:
            logger.error(f"Failed to save auth codes to disk: {e}")

    def register_client(self, client: OAuthClientInformationFull):
        """Register a new client and persist to disk."""
        # Ensure client has default scopes if not specified
        # This is critical for authorization validation in MCP
        if client.scope is None:
            # Create a new client object with default scopes
            client_data = {
                "client_id": client.client_id,
                "client_name": client.client_name,
                "redirect_uris": client.redirect_uris,
                "grant_types": client.grant_types,
                "scope": "read write payment account",  # Default scopes
            }
            if hasattr(client, 'client_secret_hash') and client.client_secret_hash:
                client_data["client_secret_hash"] = client.client_secret_hash
            client = OAuthClientInformationFull(**client_data)
            logger.info(f"Assigned default scopes to client: {client.client_id}")
        
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
    
    def add_access_token(self, token: AccessToken):
        """Add an access token and persist to disk."""
        with self._lock:
            self.access_tokens[token.token] = token
        self._save_access_tokens()
    
    def remove_refresh_token(self, token_value: str):
        """Remove a refresh token and update disk."""
        with self._lock:
            if token_value in self.refresh_tokens:
                del self.refresh_tokens[token_value]
        self._save_refresh_tokens()

    def remove_access_token(self, token_value: str):
        """Remove an access token and update disk."""
        with self._lock:
            if token_value in self.access_tokens:
                del self.access_tokens[token_value]
        self._save_access_tokens()
    
    def save_auth_code(self, key: str, code: AuthorizationCode):
        """Save an authorization code (pending or complete) and update disk."""
        with self._lock:
            self.auth_codes[key] = code
        self._save_auth_codes()

    def delete_auth_code(self, key: str):
        """Delete an authorization code and update disk."""
        with self._lock:
            if key in self.auth_codes:
                del self.auth_codes[key]
        self._save_auth_codes()

    def clear_expired_tokens(self):
        """Remove expired tokens from memory and disk."""
        current_time = time.time()
        
        # Clear expired authorization codes (also updates disk)
        expired_codes = [
            code for code, auth_code in self.auth_codes.items()
            if not code.startswith("pending_") and auth_code.expires_at < current_time
        ]
        if expired_codes:
            with self._lock:
                for code in expired_codes:
                    del self.auth_codes[code]
            self._save_auth_codes()
            logger.info(f"Cleared {len(expired_codes)} expired auth codes")
        
        # Clear expired access tokens (also updates disk)
        expired_access = [
            token for token, access_token in self.access_tokens.items()
            if access_token.expires_at < current_time
        ]
        if expired_access:
            with self._lock:
                for token in expired_access:
                    del self.access_tokens[token]
            self._save_access_tokens()
            logger.info(f"Cleared {len(expired_access)} expired access tokens")
        
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
