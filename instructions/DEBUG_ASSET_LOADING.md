# Debug Asset Loading Issues

## Quick Diagnostic Steps

Run these commands in order to find the problem:

### Step 1: Check if your server is running

```bash
curl http://localhost:8000/health
```

**Expected output:**
```json
{"status":"healthy","service":"att-mcp-server",...}
```

**If it fails:** Your server isn't running. Start it:
```bash
cd att_server_python
python main.py
```

---

### Step 2: Check if Cloudflare tunnel is running

Look for the cloudflared terminal window. You should see:
```
Your quick Tunnel has been created! Visit it at:
https://restrictions-duncan-parties-activation.trycloudflare.com
```

**If you don't see this:** Restart cloudflared:
```bash
cloudflared tunnel --url http://localhost:8000
```

**IMPORTANT:** If the URL is different than what's in your `.env`, copy the NEW URL and update `.env`!

---

### Step 3: Verify the tunnel URL matches

```bash
# Check what's in your .env
cat att_server_python/.env | grep SERVER_URL

# Check what cloudflared says
# Look at the cloudflared terminal for the actual URL
```

**These must match EXACTLY!**

---

### Step 4: Test the tunnel externally

```bash
# Replace with YOUR actual Cloudflare URL
curl https://restrictions-duncan-parties-activation.trycloudflare.com/health
```

**Expected:** Same JSON as Step 1

**If it fails:** 
- Cloudflare tunnel isn't running
- Or the URL has changed
- Or the tunnel isn't connected to your server

---

### Step 5: Test assets through the tunnel

```bash
# Replace with YOUR actual Cloudflare URL
curl https://restrictions-duncan-parties-activation.trycloudflare.com/assets/
```

**Expected:** HTML listing of files

**If it fails:** Server isn't serving assets correctly

---

### Step 6: Check what URL the browser is trying to use

Open browser DevTools (F12), go to Network tab, and look at the failed request for `att-store-finder-2d2b.css`

The **Request URL** will show you what domain the browser is trying to reach.

Compare it to:
1. Your Cloudflare tunnel URL
2. Your SERVER_URL in .env

**If they don't match:** That's your problem!

---

## Common Problems & Solutions

### Problem: Server shows old URL with "hhttps://"

**Solution:**
```bash
# Stop the server (Ctrl+C)
# Verify .env is correct
cat att_server_python/.env

# Restart server
cd att_server_python
python main.py

# Look for this line:
# INFO:__main__:Server URL configured as: https://...
# Make sure it has only ONE 'h' in 'https'
```

---

### Problem: Cloudflare URL changed

Cloudflare quick tunnels generate a new random URL each time you start `cloudflared`.

**Solution:**
```bash
# 1. Look at cloudflared terminal for current URL
# 2. Update .env with the NEW URL
cd att_server_python
nano .env
# Update SERVER_URL=https://new-url.trycloudflare.com

# 3. Restart Python server
python main.py

# 4. Update ChatGPT connector with new URL
```

---

### Problem: Browser cached old asset URLs

**Solution:**
1. Hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
2. Or: Clear ChatGPT cache, close and reopen browser
3. Or: Open in incognito/private window

---

### Problem: Assets URL in HTML is wrong

**Check what the server generated:**

```bash
# Look at server logs when it starts
# Should see:
# DEBUG:__main__:Modifying HTML paths to use assets URL: https://your-url.trycloudflare.com/assets/
```

If the URL is wrong, the server is using an old .env value.

**Fix:**
1. Verify .env has correct URL
2. **Completely stop the server** (Ctrl+C)
3. Start fresh: `python main.py`
4. Check the log line again

---

## Visual Debugging Checklist

```
┌─────────────────────────────────────────────┐
│ Cloudflared Terminal                        │
│ Running? [YES/NO]                           │
│ URL: https://abc.trycloudflare.com          │
└─────────────────────────────────────────────┘
                    ↓
                    Does this match?
                    ↓
┌─────────────────────────────────────────────┐
│ .env file                                   │
│ SERVER_URL=https://abc.trycloudflare.com    │
└─────────────────────────────────────────────┘
                    ↓
                    Does this match?
                    ↓
┌─────────────────────────────────────────────┐
│ Python Server Log (when starting)           │
│ INFO: Server URL configured as:             │
│ https://abc.trycloudflare.com               │
└─────────────────────────────────────────────┘
                    ↓
                    Does this match?
                    ↓
┌─────────────────────────────────────────────┐
│ Browser Network Tab (Request URL)           │
│ https://abc.trycloudflare.com/assets/...    │
└─────────────────────────────────────────────┘
```

**All 4 must match exactly!**

---

## Nuclear Option: Fresh Restart

If nothing works:

```bash
# 1. Stop everything
# In cloudflared terminal: Ctrl+C
# In Python terminal: Ctrl+C

# 2. Start cloudflared fresh
cloudflared tunnel --url http://localhost:8000
# Note the URL!

# 3. Update .env with the NEW URL
cd att_server_python
nano .env
# SERVER_URL=https://the-new-url.trycloudflare.com

# 4. Start Python server
python main.py

# 5. Verify in the logs:
# INFO:__main__:Server URL configured as: https://the-new-url.trycloudflare.com

# 6. Test health endpoint
curl https://the-new-url.trycloudflare.com/health

# 7. Test assets
curl https://the-new-url.trycloudflare.com/assets/

# 8. Update ChatGPT connector
# Settings > Connectors > Edit your connector
# URL: https://the-new-url.trycloudflare.com/mcp

# 9. Test in ChatGPT with hard refresh (Ctrl+Shift+R)
```

---

## Still Not Working?

Share these outputs:

1. **Cloudflared URL:**
   ```bash
   # Look at cloudflared terminal, copy the URL
   ```

2. **Server URL from logs:**
   ```bash
   # Look at Python terminal, copy this line:
   # INFO:__main__:Server URL configured as: ...
   ```

3. **Browser request URL:**
   ```bash
   # Open DevTools > Network tab
   # Find failed att-store-finder-2d2b.css request
   # Copy the "Request URL"
   ```

4. **Health check result:**
   ```bash
   curl https://your-cloudflare-url.trycloudflare.com/health
   ```

With these 4 pieces of info, we can pinpoint the exact problem.
