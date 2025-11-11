# Cloudflare Tunnel - 5 Minute Quick Start

Get your AT&T ChatGPT app running with Cloudflare Tunnel in 5 minutes.

## What You're Fixing

Your errors:
- ✅ `stream canceled by remote with error code 0` → **FIXED**
- ✅ `Cannot determine default origin certificate path` → **Just a warning, ignore it**

## Step 1: Install Cloudflare Tunnel (1 min)

```bash
# macOS
brew install cloudflared

# Verify installation
cloudflared --version
```

## Step 2: Build Assets (if not done)

```bash
# From project root
pnpm run build

# Verify
ls assets/ | wc -l
# Should show ~40 files
```

## Step 3: Start Your Server (1 min)

```bash
cd att_server_python
source ../.venv/bin/activate
python main.py
```

You should see:
```
INFO:__main__:Server URL configured as: http://localhost:8000
INFO:__main__:Found 40 HTML asset files...
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Step 4: Start Cloudflare Tunnel (1 min)

**Open a NEW terminal window** and run:

```bash
cloudflared tunnel --url http://localhost:8000
```

Look for this line in the output:
```
Your quick Tunnel has been created! Visit it at:
https://restrictions-duncan-parties-activation.trycloudflare.com
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
         COPY THIS URL!
```

**Copy that entire URL** (yours will be different)

## Step 5: Configure Your Server (2 min)

```bash
# In yet another terminal
cd att_server_python

# Create .env file
cp .env.example .env

# Edit .env and update SERVER_URL
nano .env
# or
open .env
```

Change this line to your Cloudflare URL:
```env
SERVER_URL=https://restrictions-duncan-parties-activation.trycloudflare.com
```

**Save the file!**

## Step 6: Restart Your Server

Go back to the terminal running `python main.py`, press **Ctrl+C**, then:

```bash
python main.py
```

Now you should see:
```
INFO:__main__:Server URL configured as: https://restrictions-duncan-parties-activation.trycloudflare.com
```

## Step 7: Test It

Open in your browser:
```
https://your-tunnel-url.trycloudflare.com/health
```

Should return JSON:
```json
{
  "status": "healthy",
  "service": "att-mcp-server",
  "assets_available": true,
  "widgets_count": 6
}
```

Test assets:
```
https://your-tunnel-url.trycloudflare.com/assets/
```

Should show a file listing.

## Step 8: Add to ChatGPT

1. Open ChatGPT
2. Go to Settings → Connectors
3. Click "Add Connector"
4. Enter: `https://your-tunnel-url.trycloudflare.com/mcp`
5. Save
6. Start a new chat
7. Click "More" → Select your connector
8. Ask: "Find AT&T stores near me"

## Done! 🎉

Your app should now work without the stream errors.

## Understanding Those Errors

### ✅ FIXED: `stream canceled by remote with error code 0`

**What it was:** Cloudflare was closing connections because your server wasn't sending keep-alive headers.

**How we fixed it:** Updated `main.py` to include:
- Keep-alive headers
- Anti-buffering configuration
- Cloudflare-specific SSE handling

### ℹ️ IGNORE: `Cannot determine default origin certificate path`

**What it is:** Cloudflare looking for an optional certificate file.

**Impact:** None. Quick tunnels don't need certificates.

**Action:** Completely ignore this warning.

## Keeping It Running

### Two terminals must stay open:

**Terminal 1:** Python server
```bash
cd att_server_python
python main.py
```

**Terminal 2:** Cloudflare tunnel
```bash
cloudflared tunnel --url http://localhost:8000
```

### If you close the tunnel terminal:
- Your Cloudflare URL will be different when you restart
- Update `.env` with the new URL
- Restart the Python server
- Update ChatGPT connector with new URL

## Want a Persistent URL?

See `CLOUDFLARE_TUNNEL_SETUP.md` for instructions on creating a **named tunnel** with a URL that never changes.

## Troubleshooting

### Tunnel connects but ChatGPT shows blank widget
1. Check: `https://your-url.trycloudflare.com/health`
2. Verify `.env` has correct URL
3. Restart Python server
4. Clear ChatGPT cache (refresh page)

### "Assets directory not found"
```bash
pnpm run build
```

### Port 8000 already in use
```bash
lsof -i :8000
kill -9 <PID>
```

### Need more help?
- See `TROUBLESHOOTING.md` for detailed solutions
- See `CLOUDFLARE_TUNNEL_SETUP.md` for advanced setup
- See `QUICK_FIX.md` for common errors
