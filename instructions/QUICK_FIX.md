# Quick Fix Reference Card

## Most Common Error: Asset Loading Failures

### Symptoms:
- CSS/JS files return 404 or ERR_NAME_NOT_RESOLVED
- Widget appears blank or unstyled in ChatGPT
- Console shows: `att-store-finder-2d2b.js: Failed to load resource`

### Quick Fix with Cloudflare Tunnel (5 steps):

```bash
# 1. Build assets (if not done)
pnpm run build

# 2. Start your server
cd att_server_python
python main.py

# 3. Start Cloudflare Tunnel (in separate terminal)
cloudflared tunnel --url http://localhost:8000
# Copy the HTTPS URL (e.g., https://abc-xyz.trycloudflare.com)

# 4. Create .env file with your tunnel URL
cd att_server_python
cp .env.example .env
# Edit .env: SERVER_URL=https://your-url.trycloudflare.com

# 5. Restart server
python main.py
```

### Alternative: Using ngrok

```bash
# 3. Start ngrok instead
ngrok http 8000
# Copy the HTTPS URL (e.g., https://abc123.ngrok-free.app)
# Note: Free URLs expire every 2 hours
```

## Browser Extension Errors (Can Ignore)

### Symptoms:
```
content_script.js:1 Uncaught TypeError: Cannot read properties of undefined (reading 'control')
```

### Fix:
**These are NOT your code's errors!** They come from password managers (1Password, LastPass) and don't affect functionality.

**Test workaround:** Use incognito mode or disable extensions.

## React Hydration Error #418

### Symptoms:
```
RecoverableError: Minified React error #418
```

### Fix:
1. Disable browser extensions (Grammarly, translators, etc.)
2. Test in incognito mode
3. Refresh the ChatGPT page

## Asset Build Failed

### Symptoms:
```
ERROR: Assets directory not found
```

### Fix:
```bash
# Install dependencies first
pnpm install

# Then build
pnpm run build

# Verify
ls assets/ | wc -l
# Should show ~40
```

## Server Won't Start

### Check:
1. Python virtual environment activated?
   ```bash
   source .venv/bin/activate
   ```

2. Dependencies installed?
   ```bash
   pip install -r att_server_python/requirements.txt
   ```

3. Port 8000 available?
   ```bash
   lsof -i :8000
   # If something is using it, kill the process or use a different port
   ```

## Cloudflare Stream Error

### Symptoms:
```
ERR error="stream 13 canceled by remote with error code 0"
```

### Fix:
✅ Already fixed in updated code! Just restart your server:

```bash
cd att_server_python
# Stop server (Ctrl+C), then:
python main.py
```

The updated `main.py` now includes Cloudflare-specific headers.

## Cloudflare Certificate Warning

### Symptoms:
```
ERR Cannot determine default origin certificate path
```

### Fix:
**Ignore it!** This is just a warning, not an error. Quick tunnels work without certificates.

## ChatGPT Can't Connect

### Checklist:
- [ ] Tunnel running? (`cloudflared tunnel --url http://localhost:8000` or `ngrok http 8000`)
- [ ] SERVER_URL in `.env` matches tunnel URL exactly?
- [ ] Server restarted after changing `.env`?
- [ ] ChatGPT connector URL is `https://your-tunnel-url.trycloudflare.com/mcp`?
- [ ] Assets accessible at `https://your-tunnel-url.trycloudflare.com/assets/`?
- [ ] Health check works? `curl https://your-tunnel-url.trycloudflare.com/health`

## Emergency Reset

```bash
# Stop everything
pkill -f python
pkill -f ngrok

# Clean rebuild
rm -rf assets/ node_modules/ .venv/
pnpm install
pnpm run build
python -m venv .venv
source .venv/bin/activate
pip install -r att_server_python/requirements.txt

# Fresh start
cd att_server_python
cp .env.example .env
# Edit .env with your ngrok URL
python main.py
```

## Verification Commands

```bash
# Check assets exist
ls -la assets/*.html | head -5

# Check server responds
curl http://localhost:8000/assets/

# Check ngrok URL works
curl https://your-url.ngrok-free.app/assets/

# Check MCP endpoint
curl http://localhost:8000/mcp
```

## When to Read Full Docs

- ✅ Quick fixes didn't work
- ✅ Need to understand the architecture
- ✅ Want to customize widgets
- ✅ Deploying to production

See: `SETUP_GUIDE.md` and `TROUBLESHOOTING.md`
