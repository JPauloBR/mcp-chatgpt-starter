# Troubleshooting Guide

This guide helps resolve common errors when running the AT&T MCP ChatGPT app.

## Table of Contents
- [Common ChatGPT Browser Errors](#common-chatgpt-browser-errors)
- [Asset Loading Errors](#asset-loading-errors)
- [React Hydration Errors](#react-hydration-errors)
- [Server Configuration Issues](#server-configuration-issues)

---

## Common ChatGPT Browser Errors

### Error: `content_script.js: Cannot read properties of undefined (reading 'control')`

**Type:** Browser Extension Interference

**Explanation:** This error comes from browser extensions (typically password managers like 1Password, LastPass, Dashlane, or Grammarly) that inject scripts into web pages. These extensions try to interact with form fields on the ChatGPT page and sometimes cause JavaScript errors.

**Solution:**
1. **Not your code** - These errors are external and typically don't break your app
2. To test if your app works correctly, try:
   - Open an incognito/private browser window
   - Disable browser extensions temporarily
   - Use a different browser
3. If your app functions despite these errors, you can safely ignore them

**Prevention:**
- Use incognito mode for development
- Disable unnecessary browser extensions when testing

---

## Asset Loading Errors

### Error: `Failed to load resource: net::ERR_NAME_NOT_RESOLVED` or 404 on CSS/JS files

**Example:**
```
att-store-finder-2d2b.css:1 Failed to load resource: net::ERR_NAME_NOT_RESOLVED
att-store-finder-2d2b.js:1 Failed to load resource: net::ERR_NAME_NOT_RESOLVED
```

**Root Cause:** The HTML is trying to load assets from an incorrect domain or the `SERVER_URL` environment variable is misconfigured.

**Solution:**

1. **Check if assets are built:**
   ```bash
   ls -la assets/
   ```
   If empty, run:
   ```bash
   pnpm run build
   ```

2. **Verify SERVER_URL configuration:**
   ```bash
   cd att_server_python
   cat .env
   ```
   
   The `.env` file should contain:
   ```env
   # For local development
   SERVER_URL=http://localhost:8000
   
   # For ngrok (when testing with ChatGPT)
   SERVER_URL=https://your-ngrok-url.ngrok-free.app
   ```

3. **If using ngrok:**
   - Start ngrok: `ngrok http 8000`
   - Copy the HTTPS URL (e.g., `https://abc123.ngrok-free.app`)
   - Update `.env`: `SERVER_URL=https://abc123.ngrok-free.app`
   - Restart the Python server

4. **Verify assets are accessible:**
   Open in browser:
   - Local: `http://localhost:8000/assets/`
   - Ngrok: `https://your-url.ngrok-free.app/assets/`
   
   You should see a directory listing of asset files.

5. **Check server logs:**
   When starting the server, you should see:
   ```
   INFO:__main__:Server URL configured as: http://localhost:8000
   INFO:__main__:Found 40 HTML asset files in /path/to/assets
   ```

**Common Mistakes:**
- Forgetting to rebuild assets after code changes (`pnpm run build`)
- Using HTTP instead of HTTPS for ngrok URLs
- Not restarting the server after changing `.env`
- Ngrok session expired (free tier URLs expire after 2 hours)

---

## React Hydration Errors

### Error: `RecoverableError: Minified React error #418`

**Explanation:** This occurs when React tries to "hydrate" (attach event handlers to) server-rendered HTML but finds a mismatch between what was rendered and what React expects.

**Common Causes:**
1. Browser extensions modifying the DOM (e.g., Grammarly, translate extensions)
2. Inconsistent rendering between server and client
3. Using browser-only APIs during server-side rendering

**Solution:**

1. **Check browser console for the full error:**
   - Visit: `https://react.dev/errors/418`
   - This will show the unminified error message

2. **Disable browser extensions** that modify page content:
   - Grammarly
   - Translation extensions
   - Ad blockers (some modify DOM)
   - Dark mode extensions

3. **If developing the widget:**
   - Ensure components render consistently on server and client
   - Use `useEffect` for browser-only code
   - Avoid direct DOM manipulation

4. **Test in incognito mode** to rule out extension interference

---

## Server Configuration Issues

### Error: `Assets directory not found`

**Message:**
```
ERROR:__main__:Assets directory not found: /path/to/assets
ERROR:__main__:Please run 'pnpm run build' to generate assets before starting the server.
```

**Solution:**
```bash
# From project root
pnpm install
pnpm run build

# Verify assets were created
ls -la assets/
```

---

### Warning: `SERVER_URL not set in .env file`

**Message:**
```
WARNING:__main__:SERVER_URL not set in .env file. Using default: http://localhost:8000.
```

**Impact:** 
- Works fine for local testing
- **Will fail** when using with ChatGPT (ChatGPT can't access localhost)

**Solution for ChatGPT integration:**

1. **Create `.env` file:**
   ```bash
   cd att_server_python
   cp .env.example .env
   ```

2. **Start ngrok:**
   ```bash
   ngrok http 8000
   ```

3. **Update `.env` with your ngrok URL:**
   ```env
   SERVER_URL=https://abc123.ngrok-free.app
   ```

4. **Restart the server:**
   ```bash
   cd att_server_python
   python main.py
   ```

---

## Cloudflare Tunnel Errors

### Error: `stream canceled by remote with error code 0`

**Full error:**
```
ERR error="stream 13 canceled by remote with error code 0"
ERR Request failed error="stream 13 canceled by remote with error code 0"
```

**Cause:** Cloudflare closing connections due to:
- Missing keep-alive headers
- Buffering issues with Server-Sent Events
- Connection timeouts

**Solution:** ✅ Already fixed in the updated `main.py`

The server now includes:
- Keep-alive headers
- Anti-buffering configuration
- Proper SSE handling for Cloudflare

**If still occurring:**
1. Restart your Python server (to load the updated code)
2. Verify you're using the latest `main.py`
3. Check server logs for any other errors

### Warning: `Cannot determine default origin certificate path`

**Message:**
```
ERR Cannot determine default origin certificate path. No file cert.pem
```

**Impact:** None - this is just a warning

**Explanation:** Cloudflare is looking for an optional certificate file that's only needed for named tunnels with custom domains. Quick tunnels work fine without it.

**Action:** Can safely ignore this warning

---

## CORS and Gravatar Errors

### Error: `Access to image at 'gravatar.com' has been blocked by CORS`

**Explanation:** ChatGPT is trying to load your profile picture from Gravatar, but CORS policies block it. This is a ChatGPT platform issue, not your app.

**Impact:** None on your app functionality

**Solution:** Ignore these errors - they're cosmetic and don't affect functionality

---

## 404 Errors on Backend API

### Error: `/backend-api/ecosystem/widget?uri=...` 404

**Example:**
```
/backend-api/ecosystem/widget?uri=connectors%3A%2F%2F... Failed to load resource: the server responded with a status of 404
```

**Explanation:** ChatGPT's platform is looking for additional metadata about your connector. This can happen during initial setup or when the connector isn't fully registered.

**Solution:**
1. Ensure your connector is properly added in ChatGPT Settings > Connectors
2. Use the full MCP endpoint URL (e.g., `https://your-url.ngrok-free.app/mcp`)
3. Wait a few moments for ChatGPT to cache connector metadata
4. Refresh the ChatGPT page

---

## Quick Diagnostic Checklist

When things aren't working, check these in order:

- [ ] Assets are built: `ls assets/ | wc -l` (should show ~40 files)
- [ ] Server is running: `curl http://localhost:8000/assets/` (should return HTML)
- [ ] `.env` file exists with correct `SERVER_URL`
- [ ] If using ngrok: URL in `.env` matches ngrok output
- [ ] Browser extensions disabled (for testing)
- [ ] Server restarted after `.env` changes
- [ ] ChatGPT connector configured with correct URL

---

## Getting More Help

If issues persist:

1. **Check server logs** for specific error messages
2. **Inspect network tab** in browser DevTools to see failed requests
3. **Verify asset URLs** by checking the HTML source in browser
4. **Test with minimal setup** (disable extensions, use incognito)

**Enable debug logging:**
```python
# In att_server_python/main.py, change:
logging.basicConfig(level=logging.DEBUG)  # Instead of INFO
```

This will show detailed information about path replacements and asset loading.
