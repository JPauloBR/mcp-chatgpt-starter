# OAuth Quick Start - 5 Minutes

Get OAuth authentication running with your AT&T MCP Server in 5 minutes.

## Prerequisites

- Python 3.10+ installed
- Cloudflare tunnel or ngrok for HTTPS
- ChatGPT Developer Mode enabled

---

## Step 1: Update Configuration (1 min)

Create `.env` file in `att_server_python/`:

```bash
cd att_server_python
cp .env.example .env
```

Edit `.env`:
```bash
# Your persistent domain
SERVER_URL=https://att-mcp.jpaulo.io

# Enable OAuth
OAUTH_ENABLED=true
OAUTH_ISSUER_URL=https://att-mcp.jpaulo.io
OAUTH_VALID_SCOPES=read,write,payment,account
OAUTH_DEFAULT_SCOPES=read
```

---

## Step 2: Install Dependencies (1 min)

```bash
cd att_server_python
pip install -r requirements.txt
```

This installs the new `jinja2` dependency for OAuth templates.

---

## Step 3: Start Server (30 sec)

```bash
python main.py
```

Look for these logs:
```
INFO:__main__:OAuth enabled: True
INFO:__main__:OAuth provider initialized
INFO:__main__:OAuth endpoints registered
```

---

## Step 4: Setup Cloudflare Tunnel (1 min)

```bash
# Start tunnel pointing to your domain
cloudflared tunnel --url http://localhost:8000
```

Or if you have a named tunnel configured:
```bash
cloudflared tunnel run att-mcp
```

Verify it's working:
```bash
curl https://att-mcp.jpaulo.io/health | jq
```

---

## Step 5: Test OAuth Endpoints (1 min)

```bash
# Test OAuth metadata
curl https://att-mcp.jpaulo.io/.well-known/oauth-authorization-server | jq

# Test OAuth stats
curl https://att-mcp.jpaulo.io/oauth/stats | jq

# Test authorization page (in browser)
open "https://att-mcp.jpaulo.io/oauth/authorize/page?client_id=test&redirect_uri=https://example.com"
```

---

## Step 6: Add to ChatGPT (1 min)

1. Open ChatGPT Settings → Connectors
2. Click "Add Connector"
3. Enter: `https://att-mcp.jpaulo.io/mcp`
4. Save

ChatGPT will:
- Detect OAuth is required
- Redirect you to authorization page
- Show consent screen
- Exchange tokens automatically

Click "Authorize" when prompted.

---

## Step 7: Test It (30 sec)

In ChatGPT:
1. Start new chat
2. Click "More" → Select your connector
3. Ask: "Find AT&T stores near me"

You should see the widget load with OAuth authentication active!

---

## Verify OAuth is Working

Check server logs for:
```
INFO:oauth_provider:Registered client: <client_id>
INFO:oauth_provider:Generated authorization code for client: <client_id>
INFO:oauth_provider:Exchanged authorization code for tokens
```

Check stats:
```bash
curl https://att-mcp.jpaulo.io/oauth/stats | jq
```

Expected output:
```json
{
  "oauth_enabled": true,
  "clients": 1,
  "authorization_codes": 0,
  "access_tokens": 1,
  "refresh_tokens": 1
}
```

---

## Troubleshooting

### "OAuth not enabled"
- Check `.env` has `OAUTH_ENABLED=true`
- Restart server after changing `.env`

### "Authorization page not found"
- Ensure `templates/authorize.html` exists
- Check file permissions

### "Tokens not working"
- Tokens are in-memory (lost on restart)
- Check token hasn't expired (1 hour default)
- Review server logs for errors

### ChatGPT can't connect
- Verify HTTPS is working: `curl https://att-mcp.jpaulo.io/health`
- Check Cloudflare tunnel is running
- Ensure no firewall blocking port 8000

---

## What's Next?

✅ **Phase 1 Complete**: Demo OAuth provider working  
🔄 **Test thoroughly**: Try different scopes and flows  
📖 **Read full guide**: See `OAUTH_SETUP_GUIDE.md`  
⏳ **Phase 2**: Generic OAuth providers (Auth0, Google, etc.)  

---

## Key Files

- `att_server_python/oauth_provider.py` - OAuth implementation
- `att_server_python/templates/authorize.html` - Consent UI
- `att_server_python/main.py` - OAuth integration
- `att_server_python/.env` - Configuration
- `instructions/OAUTH_SETUP_GUIDE.md` - Complete documentation

---

## Support

If something isn't working:
1. Check server logs: Look for ERROR or WARNING messages
2. Test endpoints: `curl https://att-mcp.jpaulo.io/oauth/stats`
3. Review documentation: `OAUTH_SETUP_GUIDE.md`
4. Check tunnel is active: `curl https://att-mcp.jpaulo.io/health`

---

**That's it! OAuth is now protecting your MCP server.** 🎉
