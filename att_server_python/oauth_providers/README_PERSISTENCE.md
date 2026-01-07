# OAuth Persistent Storage

## Overview

The OAuth providers now use persistent storage for client registrations and refresh tokens. This ensures that ChatGPT and other clients can reconnect after server restarts without needing to re-register.

## What's Persisted

- **Client Registrations**: All registered OAuth clients (including their client IDs, secrets, and redirect URIs)
- **Refresh Tokens**: Long-lived refresh tokens that allow clients to obtain new access tokens

## What's NOT Persisted (Intentionally)

- **Authorization Codes**: Short-lived (10 minutes), stored in memory only
- **Access Tokens**: Short-lived (1 hour by default), stored in memory only
- **Pending Authorizations**: Temporary state during OAuth flow, stored in memory only

## Storage Location

By default, OAuth data is stored in the `.oauth_data/` directory:

```
.oauth_data/
├── clients.json          # Client registrations
└── refresh_tokens.json   # Refresh tokens
```

## Implementation

The `PersistentStore` class (in `persistent_store.py`) provides:

- **Thread-safe operations**: Uses locks to prevent concurrent write issues
- **Automatic cleanup**: Expired refresh tokens are removed on load and save
- **JSON serialization**: Human-readable storage format for debugging

## Changes Made

### All OAuth Providers Updated

1. **Custom Provider** (`custom.py`): Changed from `InMemoryStore` to `PersistentStore`
2. **Google Provider** (`google.py`): Changed from `InMemoryStore` to `PersistentStore`
3. **Azure Provider** (`azure.py`): Changed from `InMemoryStore` to `PersistentStore`

### Methods Updated

Each provider now uses these persistent store methods:

- `store.register_client(client)` - Registers and persists a client
- `store.add_refresh_token(token)` - Adds and persists a refresh token
- `store.remove_refresh_token(token_value)` - Removes and updates disk

## Security Considerations

1. **Client Secrets**: Stored as hashes (handled by MCP library)
2. **Tokens**: Stored as cryptographically secure random strings
3. **File Permissions**: The `.oauth_data/` directory should be protected (mode 700)
4. **Backup**: Consider backing up `.oauth_data/` for production deployments

## Migration from In-Memory Storage

If you were using the old in-memory storage:

1. **First startup**: Server will create `.oauth_data/` directory
2. **Existing sessions**: ChatGPT will need to re-connect and re-authorize once
3. **Future restarts**: Sessions will persist automatically

## Troubleshooting

### Client Not Found Error

If you see `Client ID 'xxx' not found`:

1. Check if `.oauth_data/clients.json` exists
2. Verify the file contains your client registration
3. If corrupted, delete the file and re-register (ChatGPT will re-connect)

### Stale Refresh Tokens

Refresh tokens expire based on `OAUTH_REFRESH_TOKEN_TTL` (default 24 hours):

- Expired tokens are automatically cleaned up
- Clients will need to re-authorize after expiration

### Storage Directory Issues

If the server can't create `.oauth_data/`:

1. Check file permissions in the server directory
2. Ensure sufficient disk space
3. Check for file system errors

## Configuration

You can customize storage location by modifying `PersistentStore` initialization in each provider:

```python
# Default
self.store = PersistentStore()  # Uses .oauth_data/

# Custom location
self.store = PersistentStore(storage_dir="/path/to/oauth/data")
```

## Production Recommendations

1. **Backup Strategy**: Regularly backup `.oauth_data/` directory
2. **Monitoring**: Monitor file sizes and disk usage
3. **Cleanup**: Implement periodic cleanup of very old expired tokens
4. **Permissions**: Set directory permissions to 700 (owner read/write/execute only)
5. **Encryption**: Consider encrypting the filesystem or specific files for sensitive deployments
