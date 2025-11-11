# Fix: ChatGPT "Connector is not safe" Error

## Common Causes & Fixes

### Issue 1: MCP Endpoint Not Responding

ChatGPT needs to verify your `/mcp` endpoint responds correctly.

**Test your endpoint:**

```bash
# Replace with YOUR actual tunnel URL
curl -X POST https://your-tunnel-url.trycloudflare.com/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {
        "name": "test-client",
        "version": "1.0.0"
      }
    }
  }'
```

**Expected response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {...},
    "serverInfo": {...}
  }
}
```

**If you get an error or no response:** Your server isn't running or tunnel isn't working.

---

### Issue 2: HTTP Instead of HTTPS

ChatGPT **requires HTTPS**. HTTP URLs are considered "not safe".

**Check your connector URL:**
- ❌ `http://anything` → Not safe
- ✅ `https://your-tunnel.trycloudflare.com/mcp` → Safe

**Fix:** Make sure you're using the HTTPS URL from Cloudflare.

---

### Issue 3: Tunnel Not Running or Wrong URL

**Verify your setup:**

```bash
# 1. Check Python server is running
curl http://localhost:8000/health
# Should return: {"status":"healthy",...}

# 2. Check tunnel is running
# Look at your cloudflared terminal - should show:
# "Connection registered" or similar

# 3. Test tunnel from outside
curl https://your-tunnel-url.trycloudflare.com/health
# Should return same JSON as step 1

# 4. Test MCP endpoint through tunnel
curl -X POST https://your-tunnel-url.trycloudflare.com/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'
```

---

### Issue 4: CORS or SSL Certificate Issues

Sometimes Cloudflare tunnel certificates aren't immediately trusted.

**Try these URLs:**

```bash
# Quick tunnel URL format (if using quick tunnel)
https://abc-def-ghi.trycloudflare.com/mcp

# Named tunnel cfargotunnel.com format
https://e24ead53-de6b-47d9-9726-3a0297f84b2e.cfargotunnel.com/mcp
```

**Test in browser first:**
- Open: `https://your-tunnel-url.trycloudflare.com/health`
- You should see JSON (not a certificate error)
- If you see a certificate warning, Cloudflare hasn't provisioned the cert yet (wait a few minutes)

---

### Issue 5: MCP Protocol Version Mismatch

ChatGPT expects specific MCP protocol responses.

**Check your server logs** when you test the MCP endpoint. Look for:
```
INFO:     POST /mcp - 200 OK
```

If you see errors, the server isn't handling MCP requests correctly.

---

## Step-by-Step Fix

### Step 1: Verify Everything is Running

**Terminal 1 - Python Server:**
```bash
cd att_server_python
python main.py
```

Look for:
```
INFO:__main__:Server URL configured as: https://...
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Terminal 2 - Cloudflare Tunnel:**
```bash
# Quick tunnel (recommended for testing)
cloudflared tunnel --url http://localhost:8000

# OR named tunnel
cloudflared tunnel run e24ead53-de6b-47d9-9726-3a0297f84b2e
```

**Copy the URL** from cloudflared output.

---

### Step 2: Update Your .env

```bash
cd att_server_python
nano .env
```

Set `SERVER_URL` to match your tunnel URL **exactly**:
```env
SERVER_URL=https://your-actual-tunnel-url.trycloudflare.com
```

**Restart Python server** after changing .env!

---

### Step 3: Test the MCP Endpoint

```bash
# Replace with YOUR tunnel URL
curl -v -X POST https://your-tunnel-url.trycloudflare.com/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {
        "name": "test-client",
        "version": "1.0.0"
      }
    }
  }'
```

**What to check:**
- HTTP status should be `200 OK`
- Response should be valid JSON
- Response should contain `"jsonrpc":"2.0"`

**If you get:**
- `404` → Server is running but `/mcp` endpoint not found
- `502` or `504` → Tunnel can't reach your server
- `SSL certificate` error → Wait a few minutes for Cloudflare to provision
- `Could not resolve host` → Wrong tunnel URL

---

### Step 4: Add to ChatGPT with Correct Format

In ChatGPT Settings > Connectors:

**Connector URL:**
```
https://your-tunnel-url.trycloudflare.com/mcp
```

**Important:**
- ✅ Must be HTTPS (not HTTP)
- ✅ Must end with `/mcp`
- ✅ Must be your actual tunnel URL (not localhost)
- ✅ No trailing slash after `/mcp`

**Examples:**
- ✅ `https://abc-def.trycloudflare.com/mcp`
- ✅ `https://e24ead53-de6b-47d9-9726-3a0297f84b2e.cfargotunnel.com/mcp`
- ❌ `http://localhost:8000/mcp` (not HTTPS, not public)
- ❌ `https://abc-def.trycloudflare.com/mcp/` (trailing slash)

---

## Common Mistakes Checklist

- [ ] Used HTTP instead of HTTPS
- [ ] Python server not running
- [ ] Cloudflare tunnel not running
- [ ] Wrong tunnel URL in ChatGPT
- [ ] Tunnel URL in `.env` doesn't match actual tunnel URL
- [ ] Forgot to restart Python server after changing `.env`
- [ ] Added trailing slash: `/mcp/` instead of `/mcp`
- [ ] Using localhost URL instead of tunnel URL

---

## Quick Diagnostic Commands

Run these and share the output if still not working:

```bash
# 1. Is Python server running?
curl http://localhost:8000/health

# 2. What's in your .env?
cat att_server_python/.env | grep SERVER_URL

# 3. Is tunnel accessible?
# Replace with YOUR tunnel URL
curl https://your-tunnel-url.trycloudflare.com/health

# 4. Does MCP endpoint work?
# Replace with YOUR tunnel URL
curl -X POST https://your-tunnel-url.trycloudflare.com/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'

# 5. What URL are you using in ChatGPT?
echo "ChatGPT connector URL: https://your-tunnel-url.trycloudflare.com/mcp"
```

---

## Still Getting "Not Safe" Error?

### Try These Fixes:

**1. Wait and Retry**
Sometimes ChatGPT needs a few minutes to verify the endpoint. Wait 2-3 minutes and try again.

**2. Use a Fresh Tunnel**
```bash
# Stop current tunnel (Ctrl+C)
# Start a new quick tunnel
cloudflared tunnel --url http://localhost:8000
# Use the NEW URL in ChatGPT
```

**3. Test in Browser First**
Open this in your browser:
```
https://your-tunnel-url.trycloudflare.com/health
```

If you see a certificate error or can't access it, ChatGPT won't either.

**4. Check Server Logs**
When you try to add the connector in ChatGPT, watch your Python server logs. You should see:
```
INFO:     POST /mcp - 200 OK
```

If you see errors or no requests, ChatGPT isn't reaching your server.

**5. Verify MCP Response Format**
Your server must respond to MCP `initialize` requests. The updated `main.py` should handle this, but verify the server is running the latest code.

---

## Debug Mode

Enable debug logging to see what's happening:

```python
# In att_server_python/main.py, change line 27:
logging.basicConfig(level=logging.DEBUG)  # Change from INFO to DEBUG
```

Restart server and watch the logs when adding the connector.

---

## What ChatGPT Checks

When you add a connector, ChatGPT:
1. ✅ Verifies URL uses HTTPS
2. ✅ Tests if endpoint is reachable
3. ✅ Sends MCP `initialize` request
4. ✅ Validates response format
5. ✅ Checks SSL certificate is valid
6. ✅ Verifies no security issues

If any of these fail → "Connector is not safe"

---

## Next Steps

1. **Run the diagnostic commands** above
2. **Share the output** if you're still stuck
3. **Tell me:**
   - What tunnel URL you're using
   - What URL you entered in ChatGPT
   - What error message you see (exact text)
   - What your Python server logs show

With this info, I can pinpoint the exact issue!
