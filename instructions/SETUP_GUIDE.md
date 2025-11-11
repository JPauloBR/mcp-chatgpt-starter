# Complete Setup Guide for AT&T ChatGPT App

This guide walks you through setting up and running the AT&T MCP server for ChatGPT integration.

## Prerequisites

- Node.js 18+ and pnpm installed
- Python 3.10+
- **Cloudflare Tunnel** (recommended, free, no account needed) OR ngrok for ChatGPT testing

## Step 1: Install Dependencies

```bash
# Install Node.js dependencies
pnpm install

# Create Python virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install Python dependencies
pip install -r att_server_python/requirements.txt
```

## Step 2: Build Assets

```bash
# Build all widget assets (this creates the assets/ directory)
pnpm run build

# Verify assets were created
ls -la assets/
# You should see ~40 files including HTML, CSS, and JS files
```

## Step 3: Configure Environment

```bash
# Create .env file from example
cd att_server_python
cp .env.example .env
```

### For Local Testing Only:
Leave `.env` as is (uses `http://localhost:8000`)

### For ChatGPT Integration (Cloudflare Tunnel - Recommended):

1. **Install Cloudflare Tunnel** (if not already installed):
   ```bash
   # macOS
   brew install cloudflared
   
   # Linux/Windows: see CLOUDFLARE_TUNNEL_SETUP.md
   ```

2. **Start Cloudflare Tunnel** in a separate terminal:
   ```bash
   cloudflared tunnel --url http://localhost:8000
   ```
   
   You'll see:
   ```
   Your quick Tunnel has been created! Visit it at:
   https://restrictions-duncan-parties-activation.trycloudflare.com
   ```

3. **Copy the HTTPS URL** from the output (e.g., `https://xyz-abc.trycloudflare.com`)

4. **Update `att_server_python/.env`:**
   ```env
   SERVER_URL=https://restrictions-duncan-parties-activation.trycloudflare.com
   ```

**Why Cloudflare?**
- ✅ Free forever with no account required
- ✅ More stable than ngrok free tier
- ✅ Better performance (CDN)
- ✅ URLs persist for the session (not 2-hour expiry)

### Alternative: Using ngrok

```bash
# 1. Start ngrok
ngrok http 8000

# 2. Copy the HTTPS URL (e.g., https://abc123.ngrok-free.app)
# 3. Update .env: SERVER_URL=https://abc123.ngrok-free.app
```

**Note:** Free ngrok URLs expire every 2 hours

**Important:** 
- Always use HTTPS, not HTTP
- Don't include trailing slash
- Cloudflare tunnels persist longer than ngrok free tier

## Step 4: Start the Server

```bash
# Make sure you're in the att_server_python directory
cd att_server_python

# Start the server
python main.py
```

You should see:
```
INFO:__main__:Server URL configured as: https://abc123.ngrok-free.app
INFO:__main__:Found 40 HTML asset files in /path/to/assets
INFO:     Started server process [12345]
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Step 5: Test the Server

### Test Locally:

```bash
# In another terminal, test the health endpoint
curl http://localhost:8000/health
# Should return: {"status":"healthy",...}

# Test the assets endpoint
curl http://localhost:8000/assets/

# Test the MCP endpoint
curl http://localhost:8000/mcp
```

### Test via Cloudflare Tunnel:

Open your Cloudflare tunnel URL in a browser:
```
https://your-url.trycloudflare.com/health
https://your-url.trycloudflare.com/assets/
```

You should see:
- `/health` returns JSON with status
- `/assets/` shows a directory listing of asset files

### Test via ngrok (if using ngrok):

```
https://abc123.ngrok-free.app/health
https://abc123.ngrok-free.app/assets/
```

## Step 6: Configure ChatGPT

1. **Enable Developer Mode** in ChatGPT (if not already enabled)
   - Visit https://platform.openai.com/docs/guides/developer-mode

2. **Add Connector in ChatGPT:**
   - Go to ChatGPT Settings > Connectors
   - Click "Add Connector"
   - Enter your MCP endpoint: `https://your-tunnel-url.trycloudflare.com/mcp`
     (or `https://your-ngrok-url.ngrok-free.app/mcp` if using ngrok)
   - Save

3. **Add to Conversation:**
   - Start a new chat
   - Click "More" options
   - Select your AT&T connector

4. **Test with queries:**
   - "Find AT&T stores near me"
   - "Show me AT&T wireless plans"
   - "What cell phones are available at AT&T?"
   - "Show me personalized offers"

## Common Issues

### "Assets directory not found"
```bash
# Run the build command
pnpm run build
```

### "Failed to load resource: ERR_NAME_NOT_RESOLVED"
- Check that `SERVER_URL` in `.env` matches your ngrok URL exactly
- Restart the Python server after changing `.env`
- Verify ngrok is still running (free URLs expire)

### content_script.js errors in browser
- These are from browser extensions (1Password, etc.)
- Test in incognito mode
- These don't affect your app functionality

### Assets load but widget doesn't appear
- Check ChatGPT console for errors
- Verify the connector is added to the conversation context
- Refresh the ChatGPT page

## Development Workflow

### When making changes to widgets:

```bash
# 1. Edit source files in src/
nano src/att-store-finder/index.jsx

# 2. Rebuild assets
pnpm run build

# 3. Restart Python server
# (Press Ctrl+C in server terminal, then run python main.py again)
```

### When tunnel URL changes:

**Cloudflare (quick tunnel):**
- URL changes each time you restart `cloudflared`
- URL persists as long as cloudflared keeps running

**ngrok (free tier):**
- URL expires every 2 hours
- URL changes each time you restart ngrok

**To update:**
```bash
# 1. Note the new tunnel URL from terminal
# 2. Update .env file with new URL
# 3. Restart Python server
# 4. Update ChatGPT connector settings with new URL
```

**Pro tip:** Use Cloudflare named tunnels for persistent URLs (see CLOUDFLARE_TUNNEL_SETUP.md)

## Project Structure

```
mcp-chatgpt-starter/
├── src/                          # Widget source code (React components)
│   ├── att-store-finder/        # Store locator widget
│   ├── att-products-carousel/   # Products carousel widget
│   └── ...
├── assets/                       # Built assets (generated, gitignored)
│   ├── att-store-finder-2d2b.html
│   ├── att-store-finder-2d2b.js
│   ├── att-store-finder-2d2b.css
│   └── ...
├── att_server_python/           # MCP server
│   ├── main.py                  # Server implementation
│   ├── requirements.txt         # Python dependencies
│   ├── .env                     # Configuration (create from .env.example)
│   └── .env.example             # Example configuration
├── TROUBLESHOOTING.md           # Error solutions
└── README.md                    # Project overview
```

## Monitoring and Debugging

### Enable debug logging:

Edit `att_server_python/main.py` line 27:
```python
logging.basicConfig(level=logging.DEBUG)  # Changed from INFO
```

### Check asset paths:

Debug logs will show:
```
DEBUG:__main__:Modifying HTML paths to use assets URL: https://abc123.ngrok-free.app/assets/
DEBUG:__main__:Made 3 types of path replacements
DEBUG:__main__:Loaded widget HTML with hash: att-store-finder-2d2b.html
```

### Monitor requests:

The server logs all HTTP requests:
```
INFO:     127.0.0.1:54321 - "GET /assets/att-store-finder-2d2b.css HTTP/1.1" 200 OK
INFO:     127.0.0.1:54321 - "GET /assets/att-store-finder-2d2b.js HTTP/1.1" 200 OK
```

## Production Deployment

For production (not ngrok), deploy to a cloud provider:

1. **Deploy to your hosting platform** (AWS, GCP, Azure, Heroku, etc.)

2. **Set environment variables:**
   ```env
   SERVER_URL=https://your-production-domain.com
   ```

3. **Configure HTTPS** (required for ChatGPT integration)

4. **Update ChatGPT connector** with production URL

## Next Steps

- Customize widget data in `att_server_python/main.py`
- Create new widgets in `src/` directory
- Integrate with your backend APIs
- Add authentication if needed

## Support

For issues and troubleshooting:
- See `TROUBLESHOOTING.md` for common errors
- Check server logs for specific error messages
- Use browser DevTools Network tab to debug asset loading
