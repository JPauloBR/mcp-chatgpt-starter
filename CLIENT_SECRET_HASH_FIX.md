# Client Secret Hash Fix

## Problem Identified

The OAuth client data was being saved with `client_secret_hash: null` in the JSON file, which caused the MCP library to fail when loading the client.

### Root Cause

When saving clients to JSON, the `client_secret_hash` field was being saved as `null` instead of being omitted entirely. This caused issues when the MCP library tried to validate the loaded client object.

## Fix Applied

### 1. Updated `persistent_store.py`

**Save Function:**
- Now only includes `client_secret_hash` in JSON if it exists AND is not None
- Omits the field entirely if it's None

**Load Function:**
- Removes `client_secret_hash` from params if it's None before creating client object
- Better error handling and validation

### 2. Fixed `clients.json`

Removed the `"client_secret_hash": null` field from the stored client data.

### 3. Added Better Logging

Enhanced logging in:
- `oauth_providers/google.py` - Track Google OAuth redirects and callbacks
- `main.py` - Log Google OAuth callback endpoint hits

## Verification

Run the test script to verify client data:

```bash
cd att_server_python
python3 test_client_load.py
```

Expected output:
```
✓ client_secret_hash not present (OK)
✓ All required fields present
✓ Client data validation complete!
```

## Testing Instructions

### 1. Restart the Server

```bash
cd att_server_python
python3 main.py
```

### 2. Watch for These Log Lines

**On startup:**
```
INFO:oauth_providers.persistent_store:Loaded 1 clients from .oauth_data/clients.json
DEBUG:oauth_providers.persistent_store:Loaded client d7516cbe-97cc-46c4-9d89-ad25311a36e3: ChatGPT
```

**When ChatGPT connects:**
```
INFO:oauth_providers.google:Redirecting to Google OAuth for client d7516cbe-97cc-46c4-9d89-ad25311a36e3
DEBUG:oauth_providers.google:Callback URL will be: https://att-mcp.jpaulo.io/oauth/google/callback
```

**When Google redirects back:**
```
INFO:main:Google OAuth callback endpoint hit: ...
INFO:oauth_providers.google:Google OAuth callback received: state=...
```

### 3. Expected Behavior

✅ **If using Google OAuth provider:**
1. ChatGPT will redirect to Google login
2. You'll see the Google consent screen
3. After approval, you'll be redirected to your consent page
4. After approval, ChatGPT will connect successfully

✅ **If using custom OAuth provider:**
1. You'll see the consent page immediately
2. After approval, ChatGPT will connect successfully

## Current Configuration

Your server is configured with:
- **OAuth Provider:** google
- **Issuer URL:** https://att-mcp.jpaulo.io
- **Callback URL:** https://att-mcp.jpaulo.io/oauth/google/callback
- **Valid Client:** d7516cbe-97cc-46c4-9d89-ad25311a36e3
- **Valid Refresh Token:** Present (expires in ~24 hours)

## Important Notes

### Google OAuth Configuration

Make sure your Google Cloud Console OAuth client has this exact redirect URI:
```
https://att-mcp.jpaulo.io/oauth/google/callback
```

Common mistakes:
- ❌ `http://` instead of `https://`
- ❌ Missing `/oauth/google/callback` path
- ❌ Extra trailing slash
- ❌ Wrong domain

### If Still Having Issues

1. **Check Google Cloud Console:**
   - Verify redirect URI matches exactly
   - Check that OAuth consent screen is configured
   - Verify client ID and secret in `.env` file

2. **Check Server Logs:**
   - Look for "Redirecting to Google OAuth" log line
   - If not present, the issue is before the Google provider
   - If present but no callback, check Google Console settings

3. **Clear and Restart:**
   ```bash
   # Backup current data
   cp -r .oauth_data .oauth_data.backup
   
   # Remove OAuth data
   rm -rf .oauth_data
   
   # Restart server (will create fresh storage)
   python3 main.py
   ```
   
   Then reconnect from ChatGPT (will need to authorize once).

## Files Modified

1. `att_server_python/oauth_providers/persistent_store.py`
   - Fixed `_save_clients()` method
   - Fixed `_load_clients()` method

2. `att_server_python/.oauth_data/clients.json`
   - Removed null `client_secret_hash` field

3. `att_server_python/oauth_providers/google.py`
   - Added detailed logging

4. `att_server_python/main.py`
   - Added callback endpoint logging

## Next Steps

1. ✅ Restart your server
2. ✅ Try connecting from ChatGPT
3. ✅ Check logs for the new log lines
4. ✅ Report back with any errors you see

The fix ensures that OAuth client data is properly serialized and deserialized without corruption.
