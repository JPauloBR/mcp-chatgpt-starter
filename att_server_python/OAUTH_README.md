# OAuth Implementation for AT&T MCP Server

This directory contains the OAuth authentication implementation for the ChatGPT Apps SDK.

## 📁 Files

### Core Implementation
- **`oauth_provider.py`** - In-memory OAuth 2.0 authorization server
  - Dynamic client registration
  - Authorization code flow with PKCE
  - Token generation and validation
  - Token refresh and revocation
  - Automatic token expiry cleanup

### Integration
- **`main.py`** - FastMCP server with OAuth integration
  - OAuth configuration from environment variables
  - Authorization endpoint routes
  - OAuth stats endpoint for monitoring
  - Token verification middleware (provided by MCP library)

### Templates
- **`templates/authorize.html`** - OAuth authorization consent page
  - Modern, responsive UI
  - Displays requested scopes
  - Client information
  - Approve/Deny actions

### Configuration
- **`.env.example`** - OAuth configuration template
- **`requirements.txt`** - Updated with `jinja2` for templates

## 🚀 Quick Start

```bash
# 1. Configure OAuth
cp .env.example .env
# Edit .env: Set OAUTH_ENABLED=true and configure URLs

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start server
python main.py

# 4. Test OAuth
curl https://att-mcp.jpaulo.io/oauth/stats | jq
```

See [`../instructions/OAUTH_QUICK_START.md`](../instructions/OAUTH_QUICK_START.md) for complete setup.

## 🔐 OAuth Flow

```
┌─────────────┐                                     ┌──────────────┐
│   ChatGPT   │                                     │  MCP Server  │
│   Client    │                                     │  (OAuth AS)  │
└──────┬──────┘                                     └──────┬───────┘
       │                                                   │
       │  1. Discover OAuth endpoints                     │
       │─────────────────────────────────────────────────►│
       │  GET /.well-known/oauth-authorization-server     │
       │                                                   │
       │  2. Register client (dynamic registration)       │
       │─────────────────────────────────────────────────►│
       │  POST /register                                   │
       │  { redirect_uris, client_name, ... }             │
       │◄─────────────────────────────────────────────────│
       │  { client_id, client_secret }                    │
       │                                                   │
       │  3. Authorization request                        │
       │─────────────────────────────────────────────────►│
       │  GET /authorize?client_id=...&code_challenge=... │
       │                                                   │
       │  4. Redirect to consent page                     │
       │◄─────────────────────────────────────────────────│
       │  302 → /oauth/authorize/page?...                 │
       │                                                   │
       │  5. User approves (consent UI)                   │
       │─────────────────────────────────────────────────►│
       │  POST /oauth/authorize/approve                   │
       │                                                   │
       │  6. Redirect with authorization code             │
       │◄─────────────────────────────────────────────────│
       │  302 → redirect_uri?code=...&state=...           │
       │                                                   │
       │  7. Exchange code for tokens                     │
       │─────────────────────────────────────────────────►│
       │  POST /token                                      │
       │  { code, code_verifier, ... }                    │
       │◄─────────────────────────────────────────────────│
       │  { access_token, refresh_token, expires_in }     │
       │                                                   │
       │  8. Call MCP tools with Bearer token             │
       │─────────────────────────────────────────────────►│
       │  POST /mcp                                        │
       │  Authorization: Bearer <access_token>            │
       │◄─────────────────────────────────────────────────│
       │  Tool response                                    │
       │                                                   │
       │  9. Refresh token when expired                   │
       │─────────────────────────────────────────────────►│
       │  POST /token (grant_type=refresh_token)          │
       │◄─────────────────────────────────────────────────│
       │  { access_token, refresh_token, ... }            │
       │                                                   │
```

## 🔧 Configuration

### Environment Variables

```bash
# Enable OAuth
OAUTH_ENABLED=true

# OAuth server URL (must be HTTPS for production)
OAUTH_ISSUER_URL=https://att-mcp.jpaulo.io

# Scopes
OAUTH_VALID_SCOPES=read,write,payment,account
OAUTH_DEFAULT_SCOPES=read
```

### Token Lifetimes

Default values (configurable in `main.py`):
- **Authorization Code**: 10 minutes
- **Access Token**: 1 hour
- **Refresh Token**: 24 hours

### Scopes

| Scope | Description | Default |
|-------|-------------|---------|
| `read` | View products, services, stores | ✅ |
| `write` | Modify account preferences | ❌ |
| `payment` | Process payments | ❌ |
| `account` | Access account information | ❌ |

## 📊 Monitoring

### OAuth Statistics Endpoint

```bash
curl https://att-mcp.jpaulo.io/oauth/stats | jq
```

Returns:
```json
{
  "oauth_enabled": true,
  "issuer_url": "https://att-mcp.jpaulo.io",
  "valid_scopes": ["read", "write", "payment", "account"],
  "default_scopes": ["read"],
  "clients": 1,
  "authorization_codes": 0,
  "access_tokens": 1,
  "refresh_tokens": 1
}
```

### Server Logs

OAuth events are logged at INFO level:
```
INFO:oauth_provider:Registered client: abc123
INFO:oauth_provider:Generated authorization code for client: abc123
INFO:oauth_provider:Exchanged authorization code for tokens
INFO:oauth_provider:Access token valid: xyz789... (client: abc123)
```

## 🧪 Testing

### 1. Test OAuth Metadata
```bash
curl https://att-mcp.jpaulo.io/.well-known/oauth-authorization-server
```

### 2. Test Authorization Page
```bash
open "https://att-mcp.jpaulo.io/oauth/authorize/page?client_id=test&redirect_uri=https://example.com"
```

### 3. Manual OAuth Flow (for development)
```bash
# Step 1: Register client
curl -X POST https://att-mcp.jpaulo.io/register \
  -H "Content-Type: application/json" \
  -d '{"redirect_uris":["http://localhost:3000/callback"],"client_name":"Test Client"}'

# Step 2: Get authorization code (in browser)
open "https://att-mcp.jpaulo.io/authorize?client_id=<CLIENT_ID>&redirect_uri=http://localhost:3000/callback&response_type=code&code_challenge=<CHALLENGE>&code_challenge_method=S256"

# Step 3: Exchange code for token
curl -X POST https://att-mcp.jpaulo.io/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=authorization_code&code=<CODE>&redirect_uri=http://localhost:3000/callback&code_verifier=<VERIFIER>&client_id=<CLIENT_ID>"
```

## 🏗️ Architecture

### InMemoryOAuthProvider

```python
class InMemoryOAuthProvider(OAuthAuthorizationServerProvider):
    """
    Simple in-memory OAuth provider for demo/testing.
    
    Features:
    - Dynamic client registration
    - Authorization code generation
    - Token issuance (access + refresh)
    - Token validation and refresh
    - Token revocation
    - Automatic expiry cleanup
    
    Limitations:
    - In-memory only (lost on restart)
    - Single server instance only
    - No persistent storage
    - Auto-approves all requests (no user auth)
    """
```

### Storage

```python
@dataclass
class InMemoryStore:
    clients: Dict[str, OAuthClientInformationFull]
    auth_codes: Dict[str, AuthorizationCode]
    access_tokens: Dict[str, AccessToken]
    refresh_tokens: Dict[str, RefreshToken]
```

### Security Features

✅ PKCE (Proof Key for Code Exchange) required  
✅ 256-bit tokens (cryptographically secure)  
✅ Token rotation on refresh  
✅ Automatic token expiry  
✅ Scope validation  
✅ Client validation  
✅ State parameter support (CSRF protection)  

## ⚠️ Production Considerations

### Current Limitations (Phase 1)

🔸 **In-Memory Storage**: Tokens lost on server restart  
🔸 **No User Auth**: Auto-approves all authorization requests  
🔸 **Single Server**: Won't work across multiple instances  
🔸 **No Persistence**: Not suitable for production  

### Phase 2 Enhancements

For production deployments, Phase 2 will add:
- Persistent storage (PostgreSQL, Redis, SQLite)
- Real user authentication
- Generic OAuth provider support (Auth0, Google, Okta)
- Rate limiting
- Audit logging
- Token introspection
- Session management

## 📚 Documentation

- **[Quick Start Guide](../instructions/OAUTH_QUICK_START.md)** - 5-minute setup
- **[Complete Setup Guide](../instructions/OAUTH_SETUP_GUIDE.md)** - Full documentation
- **[ChatGPT Apps OAuth Docs](../instructions/CHATGPT-APPS-OAUTH.md)** - OpenAI reference

## 🛠️ Development

### Adding New Scopes

1. Update `.env`:
```bash
OAUTH_VALID_SCOPES=read,write,payment,account,new_scope
```

2. Update descriptions in `main.py`:
```python
scope_descriptions = {
    "new_scope": "Description of new scope",
}
```

3. Add scope checks in tool handlers (if needed)

### Customizing Token TTLs

Edit in `main.py`:
```python
oauth_provider = InMemoryOAuthProvider(
    issuer_url=OAUTH_ISSUER_URL,
    access_token_ttl=7200,      # 2 hours
    refresh_token_ttl=604800,   # 7 days
    auth_code_ttl=300,          # 5 minutes
)
```

### Custom Authorization UI

Edit `templates/authorize.html` to customize:
- Branding and colors
- Scope descriptions
- Terms and conditions
- Additional user information collection

## 🐛 Troubleshooting

### OAuth not initializing
- Check `OAUTH_ENABLED=true` in `.env`
- Restart server after config changes
- Review startup logs for errors

### Tokens not validating
- Check token hasn't expired
- Verify access token exists: `curl /oauth/stats`
- Review server logs for validation errors

### Authorization page 404
- Ensure `templates/authorize.html` exists
- Check `TEMPLATES_DIR` path in `main.py`
- Verify Jinja2 is installed

### ChatGPT connection issues
- Verify HTTPS is working
- Check OAuth metadata: `curl /.well-known/oauth-authorization-server`
- Ensure Cloudflare tunnel is running
- Review ChatGPT connector configuration

## 📖 API Reference

See `oauth_provider.py` for complete API documentation of all OAuth provider methods.

## 🤝 Contributing

When adding OAuth features:
1. Follow existing code patterns
2. Add appropriate logging
3. Update documentation
4. Test with ChatGPT Apps SDK
5. Consider security implications

## 📄 License

MIT License - See project root LICENSE file

---

**Ready to test OAuth with ChatGPT?** Follow the [Quick Start Guide](../instructions/OAUTH_QUICK_START.md)!
