# OAuth Setup Guide - ChatGPT Apps SDK

This guide covers setting up OAuth authentication for your AT&T MCP Server to work with ChatGPT Apps SDK.

## Table of Contents

- [Overview](#overview)
- [Phase 1: Demo OAuth Provider](#phase-1-demo-oauth-provider)
- [Configuration](#configuration)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Phase 2: Generic OAuth Providers](#phase-2-generic-oauth-providers)

---

## Overview

The MCP server now supports OAuth 2.0 authentication with:
- **Dynamic client registration** (ChatGPT auto-registers)
- **In-memory token storage** (suitable for testing/demos)
- **Standard OAuth 2.0 flows** (authorization code with PKCE)
- **Customizable scopes** for fine-grained access control

### OAuth Endpoints

When OAuth is enabled, the server exposes these endpoints:

| Endpoint | Purpose |
|----------|---------|
| `/.well-known/oauth-authorization-server` | OAuth metadata discovery |
| `/authorize` | Authorization endpoint (redirects to consent page) |
| `/token` | Token exchange endpoint |
| `/revoke` | Token revocation endpoint |
| `/oauth/authorize/page` | Custom consent UI page |
| `/oauth/stats` | OAuth statistics (debugging) |

---

## Phase 1: Demo OAuth Provider

### Architecture

```
┌─────────┐         ┌──────────────┐         ┌──────────────┐
│ ChatGPT │◄────────┤ MCP Server   │◄────────┤ In-Memory    │
│  Client │         │ (OAuth AS)   │         │ OAuth Store  │
└─────────┘         └──────────────┘         └──────────────┘
     │                     │
     │   1. Register       │
     │   2. Authorize      │
     │   3. Get Token      │
     │   4. Call Tools     │
     └─────────────────────┘
```

### Features

✅ Dynamic client registration  
✅ Authorization code flow with PKCE  
✅ Access token (1 hour TTL)  
✅ Refresh token (24 hour TTL)  
✅ Token rotation on refresh  
✅ Scope-based access control  
✅ Custom consent UI  

---

## Configuration

### Step 1: Update `.env` File

Create or update your `.env` file in `att_server_python/`:

```bash
# Server URL - must be HTTPS for production
SERVER_URL=https://att-mcp.jpaulo.io

# Enable OAuth
OAUTH_ENABLED=true

# OAuth Issuer URL (must match SERVER_URL for consistency)
OAUTH_ISSUER_URL=https://att-mcp.jpaulo.io

# Define available scopes
OAUTH_VALID_SCOPES=read,write,payment,account

# Default scopes when none requested
OAUTH_DEFAULT_SCOPES=read
```

### Step 2: Install Dependencies

```bash
cd att_server_python
pip install -r requirements.txt
```

New dependency: `jinja2>=3.1.0` (for authorization page templates)

### Step 3: Start the Server

```bash
python main.py
```

You should see:
```
INFO:__main__:OAuth enabled: True
INFO:__main__:OAuth issuer URL: https://att-mcp.jpaulo.io
INFO:__main__:OAuth provider initialized
INFO:__main__:OAuth endpoints registered: /oauth/authorize/page, /oauth/stats
```

### Step 4: Set Up Cloudflare Tunnel

If using Cloudflare Tunnel with your `jpaulo.io` domain:

```bash
# Named tunnel (persistent URL)
cloudflared tunnel --url http://localhost:8000 --name att-mcp
```

Or configure in your Cloudflare dashboard:
- Subdomain: `att-mcp`
- Domain: `jpaulo.io`
- Service: `http://localhost:8000`

---

## Testing

### 1. Test OAuth Metadata

```bash
curl https://att-mcp.jpaulo.io/.well-known/oauth-authorization-server | jq
```

Expected response:
```json
{
  "issuer": "https://att-mcp.jpaulo.io",
  "authorization_endpoint": "https://att-mcp.jpaulo.io/authorize",
  "token_endpoint": "https://att-mcp.jpaulo.io/token",
  "registration_endpoint": "https://att-mcp.jpaulo.io/register",
  "revocation_endpoint": "https://att-mcp.jpaulo.io/revoke",
  "scopes_supported": ["read", "write", "payment", "account"],
  ...
}
```

### 2. Test OAuth Stats

```bash
curl https://att-mcp.jpaulo.io/oauth/stats | jq
```

Expected response:
```json
{
  "oauth_enabled": true,
  "issuer_url": "https://att-mcp.jpaulo.io",
  "valid_scopes": ["read", "write", "payment", "account"],
  "default_scopes": ["read"],
  "clients": 0,
  "authorization_codes": 0,
  "access_tokens": 0,
  "refresh_tokens": 0
}
```

### 3. Add Connector to ChatGPT

1. **Enable Developer Mode** in ChatGPT
   - Visit: https://platform.openai.com/docs/guides/developer-mode

2. **Add Connector**
   - Go to: ChatGPT Settings → Connectors
   - Click: "Add Connector"
   - Enter MCP URL: `https://att-mcp.jpaulo.io/mcp`
   - Save

3. **OAuth Flow Begins**
   - ChatGPT will detect OAuth is required
   - ChatGPT registers as a client (dynamic registration)
   - ChatGPT redirects you to authorization page
   - You'll see the consent UI at `/oauth/authorize/page`
   - Click "Authorize" to grant access

4. **Use the Connector**
   - Start a new chat
   - Click "More" → Select your connector
   - Ask: "Find AT&T stores near me"
   - Tools will now require valid OAuth token

### 4. Monitor OAuth Activity

Watch server logs for OAuth events:
```
INFO:oauth_provider:Registered client: <client_id>
INFO:oauth_provider:Generated authorization code for client: <client_id>
INFO:oauth_provider:Exchanged authorization code for tokens
```

Check stats:
```bash
curl https://att-mcp.jpaulo.io/oauth/stats | jq
```

---

## OAuth Scopes

### Default Scopes

| Scope | Description | Default |
|-------|-------------|---------|
| `read` | View products, services, stores | ✅ |
| `write` | Modify account preferences | ❌ |
| `payment` | Process payments | ❌ |
| `account` | Access account information | ❌ |

### Customizing Scopes

Edit in `.env`:
```bash
# Add new scopes
OAUTH_VALID_SCOPES=read,write,payment,account,admin,reports

# Change defaults
OAUTH_DEFAULT_SCOPES=read,write
```

Update scope descriptions in `main.py`:
```python
scope_descriptions = {
    "read": "View AT&T products, services, and store locations",
    "write": "Make changes to your account and preferences",
    "payment": "Process payments on your behalf",
    "account": "Access your account information",
    "admin": "Administrative access",
    "reports": "Generate and view reports",
}
```

---

## Troubleshooting

### OAuth Not Working

**1. Check OAuth is enabled:**
```bash
curl https://att-mcp.jpaulo.io/oauth/stats
```

If `oauth_enabled: false`, check `.env`:
```bash
OAUTH_ENABLED=true
```

**2. Check OAuth metadata:**
```bash
curl https://att-mcp.jpaulo.io/.well-known/oauth-authorization-server
```

If 404, ensure:
- Server is running
- OAuth is enabled in `.env`
- No proxy/CDN caching issues

**3. Check server logs:**
```bash
# Look for these messages on startup:
INFO:__main__:OAuth enabled: True
INFO:__main__:OAuth provider initialized
INFO:__main__:OAuth endpoints registered
```

### Authorization Page Not Loading

**1. Check templates directory:**
```bash
ls att_server_python/templates/
# Should show: authorize.html
```

**2. Test authorization page directly:**
```bash
curl "https://att-mcp.jpaulo.io/oauth/authorize/page?client_id=test&redirect_uri=https://example.com"
```

### Token Issues

**1. Tokens expiring too quickly:**

Edit `main.py`:
```python
oauth_provider = InMemoryOAuthProvider(
    issuer_url=OAUTH_ISSUER_URL,
    access_token_ttl=7200,  # 2 hours (was 3600)
    refresh_token_ttl=172800,  # 48 hours (was 86400)
)
```

**2. Check token stats:**
```bash
curl https://att-mcp.jpaulo.io/oauth/stats | jq '.access_tokens'
```

**3. Clear expired tokens:**

Tokens are automatically cleared when:
- Server performs operations (lazy cleanup)
- Tokens are accessed
- New tokens are created

### ChatGPT Authorization Failed

**1. Check redirect URIs:**

ChatGPT must be in allowed redirect URIs. The MCP library handles this automatically with dynamic registration.

**2. Check CORS:**

Ensure CORS is properly configured (already done in `main.py`).

**3. Check Cloudflare settings:**

If using Cloudflare Tunnel:
- Ensure no caching for `/authorize` or `/token`
- Check Cloudflare rules aren't blocking OAuth endpoints

**4. Check server logs during authorization:**
```
INFO:oauth_provider:Registered client: <client_id>
INFO:oauth_provider:Generated authorization code
```

---

## Security Considerations

### Phase 1 Limitations

⚠️ **In-Memory Storage**: Tokens are lost on server restart  
⚠️ **No User Authentication**: Auto-approves all requests  
⚠️ **Single Server**: Won't work with multiple instances  
⚠️ **Demo Only**: Not suitable for production use  

### Production Recommendations (Phase 2)

For production deployments, consider:
1. **Persistent Storage**: PostgreSQL, Redis, or SQLite
2. **User Authentication**: Real user login/consent
3. **Rate Limiting**: Prevent abuse
4. **Token Introspection**: External token validation
5. **Audit Logging**: Track all OAuth operations
6. **Generic OAuth Providers**: Auth0, Okta, Google, etc.

---

## Phase 2: Generic OAuth Providers

Coming soon! Phase 2 will add support for:

- **Auth0** integration
- **Google OAuth** 
- **Okta** 
- **Azure AD**
- **Custom OAuth providers**

This allows your MCP server to act as an OAuth client, delegating authentication to established providers.

---

## API Reference

### OAuth Provider Methods

```python
# Get client information
client = await oauth_provider.get_client(client_id)

# Register new client
await oauth_provider.register_client(client_info)

# Create authorization code
redirect_url = await oauth_provider.authorize(client, params)

# Exchange code for tokens
tokens = await oauth_provider.exchange_authorization_code(client, auth_code)

# Refresh access token
tokens = await oauth_provider.exchange_refresh_token(client, refresh_token, scopes)

# Verify access token
access_token = await oauth_provider.load_access_token(token)

# Revoke token
await oauth_provider.revoke_token(token)

# Get statistics
stats = oauth_provider.get_stats()
```

### Token TTLs

Default token lifetimes:
- **Authorization Code**: 10 minutes
- **Access Token**: 1 hour  
- **Refresh Token**: 24 hours

Customize in `main.py`:
```python
oauth_provider = InMemoryOAuthProvider(
    issuer_url=OAUTH_ISSUER_URL,
    access_token_ttl=3600,      # seconds
    refresh_token_ttl=86400,    # seconds
    auth_code_ttl=600,          # seconds
)
```

---

## Next Steps

✅ **Phase 1 Complete**: Demo OAuth provider with in-memory storage  
🔄 **Testing**: Test with ChatGPT Apps SDK  
⏳ **Phase 2**: Add generic OAuth providers (Auth0, Google, etc.)  
⏳ **Phase 3**: Add persistent storage (PostgreSQL/Redis)  

---

## Support

For issues or questions:
1. Check server logs: `python main.py`
2. Test OAuth stats: `curl https://att-mcp.jpaulo.io/oauth/stats`
3. Review this guide's troubleshooting section
4. Check ChatGPT Apps SDK documentation

---

## Resources

- [OAuth 2.0 RFC 6749](https://datatracker.ietf.org/doc/html/rfc6749)
- [PKCE RFC 7636](https://datatracker.ietf.org/doc/html/rfc7636)
- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [ChatGPT Apps SDK Docs](https://platform.openai.com/docs/guides/apps)
