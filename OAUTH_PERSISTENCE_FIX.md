# OAuth Persistence Fix - Summary

## Problem

When trying to reconnect to the MCP server after a restart, ChatGPT was receiving this error:

```json
{
  "error": "invalid_request",
  "error_description": "Client ID '26c23f3b-4985-42a0-9d86-8f03b1a7ee3e' not found",
  "state": "oauth_s_691650fa1cbc8191978794913e248dfe"
}
```

**Root Cause**: OAuth client registrations and refresh tokens were stored in memory using `InMemoryStore`, which meant all registrations were lost when the server restarted.

## Solution

Implemented persistent storage for OAuth data using JSON files:

### Files Created

1. **`att_server_python/oauth_providers/persistent_store.py`**
   - New `PersistentStore` class that saves data to disk
   - Thread-safe operations with locks
   - Automatic cleanup of expired tokens
   - Stores data in `.oauth_data/` directory

### Files Modified

1. **`att_server_python/oauth_providers/custom.py`**
   - Changed from `InMemoryStore` to `PersistentStore`
   - Updated all refresh token operations to persist data

2. **`att_server_python/oauth_providers/google.py`**
   - Changed from `InMemoryStore` to `PersistentStore`
   - Updated all refresh token operations to persist data

3. **`att_server_python/oauth_providers/azure.py`**
   - Changed from `InMemoryStore` to `PersistentStore`
   - Updated all refresh token operations to persist data

4. **`.gitignore`**
   - Added `.oauth_data/` to prevent committing sensitive data

### Documentation Added

- **`att_server_python/oauth_providers/README_PERSISTENCE.md`**: Complete guide on the persistent storage system

## What's Persisted

✅ **Client Registrations**: All OAuth client IDs, secrets, and redirect URIs
✅ **Refresh Tokens**: Long-lived tokens for session persistence (24 hours by default)

## What's NOT Persisted

❌ **Authorization Codes**: Short-lived (10 minutes), memory-only
❌ **Access Tokens**: Short-lived (1 hour), memory-only
❌ **Pending Authorizations**: Temporary OAuth flow state, memory-only

## Testing the Fix

### Step 1: Start the Server

```bash
cd att_server_python
python3 main.py
```

The server will create a `.oauth_data/` directory on startup.

### Step 2: Connect from ChatGPT

When ChatGPT connects for the first time:

1. It will register as a new OAuth client
2. Client registration will be saved to `.oauth_data/clients.json`
3. After authorization, refresh token will be saved to `.oauth_data/refresh_tokens.json`

### Step 3: Restart the Server

```bash
# Stop with Ctrl+C, then restart
python3 main.py
```

You should see in the logs:

```
INFO:oauth_providers.persistent_store:Persistent storage initialized at .oauth_data
INFO:oauth_providers.persistent_store:Loaded X clients and Y refresh tokens
```

### Step 4: Verify Persistence

Try using ChatGPT - it should reconnect automatically without re-authorization!

## Expected Behavior

### Before the Fix ❌

- Server restart → All OAuth data lost
- ChatGPT shows: "Client ID not found" error
- User must disconnect and reconnect from ChatGPT settings
- Re-authorization required every time

### After the Fix ✅

- Server restart → OAuth data loaded from disk
- ChatGPT reconnects automatically
- No re-authorization needed
- Sessions persist across server restarts

## Monitoring

Check the storage files:

```bash
# View registered clients
cat att_server_python/.oauth_data/clients.json

# View refresh tokens (contains sensitive data!)
cat att_server_python/.oauth_data/refresh_tokens.json

# Check file sizes
ls -lh att_server_python/.oauth_data/
```

## Troubleshooting

### "Client ID not found" still appears

1. **Check if data was saved**:
   ```bash
   ls att_server_python/.oauth_data/
   cat att_server_python/.oauth_data/clients.json
   ```

2. **Verify file permissions**:
   ```bash
   ls -la att_server_python/.oauth_data/
   ```

3. **Check server logs** for errors during load:
   ```
   INFO:oauth_providers.persistent_store:Loaded X clients
   ```

### First connection after deployment

- ChatGPT will need to re-authorize once
- This is expected as no previous OAuth data exists
- Subsequent connections will work automatically

### Corrupted storage files

If JSON files become corrupted:

```bash
# Backup existing data
cp -r att_server_python/.oauth_data att_server_python/.oauth_data.backup

# Remove corrupted files
rm att_server_python/.oauth_data/*.json

# Restart server - will create fresh storage
python3 att_server_python/main.py
```

ChatGPT will need to re-authorize once.

## Security Notes

1. **Sensitive Data**: `.oauth_data/` contains client secrets and tokens
2. **Git Ignored**: Already added to `.gitignore`
3. **File Permissions**: Set to 600 (owner read/write only) automatically
4. **Backups**: Consider encrypting backups in production
5. **Directory Permissions**: Should be 700 (owner access only)

## Production Deployment

For production environments:

1. **Backup Strategy**:
   ```bash
   # Create encrypted backup
   tar czf oauth_backup_$(date +%Y%m%d).tar.gz .oauth_data
   gpg -c oauth_backup_$(date +%Y%m%d).tar.gz
   ```

2. **Monitoring**:
   - Monitor `.oauth_data/` disk usage
   - Alert on file permission changes
   - Track client registration count

3. **Rotation**:
   - Refresh tokens expire after `OAUTH_REFRESH_TOKEN_TTL` (default 24h)
   - Expired tokens are cleaned up automatically

## Configuration

Default token lifetimes (in `.env`):

```bash
OAUTH_ACCESS_TOKEN_TTL=3600        # 1 hour
OAUTH_REFRESH_TOKEN_TTL=86400      # 24 hours
OAUTH_AUTH_CODE_TTL=600            # 10 minutes
```

Increase `OAUTH_REFRESH_TOKEN_TTL` for longer-lived sessions:

```bash
OAUTH_REFRESH_TOKEN_TTL=2592000    # 30 days
```

## Next Steps

1. ✅ Restart your server
2. ✅ Test ChatGPT connection
3. ✅ Verify persistence after another restart
4. ✅ Set up backups for production
5. ✅ Monitor logs for any issues

## Questions?

See `att_server_python/oauth_providers/README_PERSISTENCE.md` for detailed technical documentation.
