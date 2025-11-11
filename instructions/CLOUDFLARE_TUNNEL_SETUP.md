# Cloudflare Tunnel Setup Guide

This guide walks you through setting up Cloudflare Tunnel (cloudflared) for exposing your AT&T MCP server to ChatGPT.

## Why Cloudflare Tunnel?

✅ **Free** - No paid plans required  
✅ **Persistent URLs** - Unlike ngrok free tier, URLs don't expire  
✅ **Better performance** - Cloudflare's global CDN  
✅ **More reliable** - Better for production use  
✅ **No account signup required** - Quick tunnels work immediately  

## Quick Start (Easiest Method)

### 1. Install Cloudflare Tunnel

**macOS (Homebrew):**
```bash
brew install cloudflared
```

**Windows:**
Download from: https://github.com/cloudflare/cloudflared/releases

**Linux:**
```bash
wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb
```

### 2. Start Your Python Server

```bash
cd att_server_python
source ../.venv/bin/activate  # If not already activated
python main.py
```

Verify it's running:
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy",...}
```

### 3. Start Cloudflare Quick Tunnel

In a **separate terminal**:

```bash
cloudflared tunnel --url http://localhost:8000
```

You'll see output like:
```
2025-11-06T20:04:30Z INF Registered tunnel connection
...
Your quick Tunnel has been created! Visit it at:
https://restrictions-duncan-parties-activation.trycloudflare.com
```

**Copy this URL!** This is your `SERVER_URL`.

### 4. Update Your .env File

```bash
cd att_server_python

# Create .env if it doesn't exist
cp .env.example .env

# Edit .env and update SERVER_URL
# Use the URL from step 3
```

Example `.env`:
```env
SERVER_URL=https://restrictions-duncan-parties-activation.trycloudflare.com
```

### 5. Restart Your Python Server

```bash
# Stop the server (Ctrl+C in the terminal running python)
# Then restart:
python main.py
```

You should see:
```
INFO:__main__:Server URL configured as: https://restrictions-duncan-parties-activation.trycloudflare.com
```

### 6. Test the Tunnel

Open in browser:
```
https://your-tunnel-url.trycloudflare.com/health
https://your-tunnel-url.trycloudflare.com/assets/
```

Both should work without errors.

### 7. Configure ChatGPT

1. Go to ChatGPT Settings > Connectors
2. Add new connector
3. Use: `https://your-tunnel-url.trycloudflare.com/mcp`
4. Save and test!

## Understanding the Errors You Saw

### ❌ Certificate Warning (Not Critical)

```
ERR Cannot determine default origin certificate path
```

**This is just a warning** - it's looking for an optional certificate file. Cloudflare Quick Tunnels work without it.

**When you need a certificate:**
- Only for named tunnels (not quick tunnels)
- For production with custom domains

### ❌ Stream Canceled Error (Fixed)

```
ERR  error="stream 13 canceled by remote with error code 0"
```

**Cause:** Cloudflare was closing the connection due to:
- Missing keep-alive headers
- Buffering issues with Server-Sent Events (SSE)
- Timeout on idle connections

**Fix:** The updated `main.py` now includes:
- Keep-alive headers
- Anti-buffering headers (`X-Accel-Buffering: no`)
- Proper SSE handling for Cloudflare
- Health check endpoint

## Quick Tunnel vs Named Tunnel

### Quick Tunnel (What you're using)
```bash
cloudflared tunnel --url http://localhost:8000
```

**Pros:**
- No configuration needed
- Start immediately
- Free forever

**Cons:**
- Random URL each time
- Must update .env and ChatGPT connector each restart
- Auto-expires after inactivity

### Named Tunnel (Production)

**Setup once, reuse forever:**

```bash
# 1. Login to Cloudflare
cloudflared tunnel login

# 2. Create named tunnel
cloudflared tunnel create att-mcp

# 3. Create config file
cat > ~/.cloudflared/config.yml <<EOF
tunnel: att-mcp
credentials-file: ~/.cloudflared/<tunnel-id>.json

ingress:
  - hostname: att-mcp.yourdomain.com
    service: http://localhost:8000
  - service: http_status:404
EOF

# 4. Route DNS
cloudflared tunnel route dns att-mcp att-mcp.yourdomain.com

# 5. Run tunnel
cloudflared tunnel run att-mcp
```

**Pros:**
- Persistent URL (no need to update .env)
- Custom subdomain
- Better for production
- Can use your own domain

**Cons:**
- Requires Cloudflare account (free)
- More setup steps
- Needs DNS configuration

## Troubleshooting Cloudflare Issues

### Tunnel connects but ChatGPT can't access

**Check:**
1. Health endpoint works: `curl https://your-url.trycloudflare.com/health`
2. Assets accessible: `curl https://your-url.trycloudflare.com/assets/`
3. SERVER_URL in `.env` matches tunnel URL exactly
4. Server restarted after changing `.env`

### "Too many requests" or rate limiting

**Solution:**
- Quick tunnels have some rate limits
- Consider upgrading to named tunnel (still free)
- Or use your own Cloudflare account

### Tunnel disconnects frequently

**Check:**
1. Python server still running?
2. Cloudflared still running?
3. Network stable?

**Quick fix:**
```bash
# Restart both
# Terminal 1:
cd att_server_python && python main.py

# Terminal 2:
cloudflared tunnel --url http://localhost:8000
```

### Assets load but widgets don't appear

**Debug steps:**
```bash
# 1. Check server logs for errors
# Look for errors in the Python terminal

# 2. Check Cloudflare logs
# Look for errors in the cloudflared terminal

# 3. Test MCP endpoint
curl -X POST https://your-url.trycloudflare.com/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'
```

### Stream timeouts after 100 seconds

**Cause:** Cloudflare's default connection timeout

**Solution (Named Tunnel):**
Add to `config.yml`:
```yaml
tunnel: att-mcp
credentials-file: ~/.cloudflared/<tunnel-id>.json
no-tls-verify: false
originRequest:
  connectTimeout: 30s
  noHappyEyeballs: false
  keepAliveConnections: 100
  keepAliveTimeout: 90s

ingress:
  - hostname: att-mcp.yourdomain.com
    service: http://localhost:8000
  - service: http_status:404
```

## Running in Production

### Keep Tunnel Running (systemd on Linux)

```bash
# Create service file
sudo nano /etc/systemd/system/cloudflared.service
```

```ini
[Unit]
Description=Cloudflare Tunnel
After=network.target

[Service]
Type=simple
User=yourusername
ExecStart=/usr/local/bin/cloudflared tunnel run att-mcp
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl enable cloudflared
sudo systemctl start cloudflared
sudo systemctl status cloudflared
```

### Keep Tunnel Running (macOS/launchd)

```bash
# Create plist file
nano ~/Library/LaunchAgents/com.cloudflare.cloudflared.plist
```

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.cloudflare.cloudflared</string>
    <key>ProgramArguments</key>
    <array>
        <string>/opt/homebrew/bin/cloudflared</string>
        <string>tunnel</string>
        <string>run</string>
        <string>att-mcp</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

```bash
# Load and start
launchctl load ~/Library/LaunchAgents/com.cloudflare.cloudflared.plist
launchctl start com.cloudflare.cloudflared
```

## Comparison: Cloudflare vs ngrok

| Feature | Cloudflare Tunnel | ngrok |
|---------|------------------|-------|
| **Free tier URL** | Random, persistent during session | Random, expires every 2 hours |
| **Setup speed** | 1 command | 1 command |
| **Account required** | No (quick tunnel) | Yes |
| **Custom domains** | Yes (free with Cloudflare) | Paid only |
| **Rate limits** | Generous | Stricter on free tier |
| **Performance** | Excellent (CDN) | Good |
| **Best for** | Production & development | Quick testing |

## Next Steps

- ✅ Tunnel working? Configure your `.env` file
- ✅ Server updated? Restart it
- ✅ Ready for production? Set up a named tunnel
- ✅ Need monitoring? Use the `/health` endpoint

## Quick Reference Commands

```bash
# Start quick tunnel
cloudflared tunnel --url http://localhost:8000

# Create named tunnel
cloudflared tunnel login
cloudflared tunnel create my-tunnel

# List tunnels
cloudflared tunnel list

# Delete tunnel
cloudflared tunnel delete my-tunnel

# Check tunnel status
cloudflared tunnel info my-tunnel
```

## Support Resources

- **Cloudflare Tunnel Docs:** https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/
- **GitHub Issues:** https://github.com/cloudflare/cloudflared/issues
- **Project Troubleshooting:** See `TROUBLESHOOTING.md` in this repo
