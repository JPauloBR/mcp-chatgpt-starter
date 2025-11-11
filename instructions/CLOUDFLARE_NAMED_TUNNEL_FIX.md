# Fix: Named Tunnel Credentials File

## The Problem

The config file has a placeholder `<tunnel-id>` that needs to be replaced with your actual tunnel ID.

## Solution - 3 Steps

### Step 1: Find Your Tunnel ID

```bash
cloudflared tunnel list
```

You'll see output like:
```
ID                                   NAME       CREATED
a1b2c3d4-5678-90ab-cdef-1234567890ab att-mcp    2025-11-07T11:40:00Z
```

**Copy the ID** (the long UUID, e.g., `a1b2c3d4-5678-90ab-cdef-1234567890ab`)

### Step 2: Find Your Credentials File

```bash
ls -la ~/.cloudflared/
```

Look for a `.json` file with a UUID name:
```
-rw-------  1 jpaulobr  staff   a1b2c3d4-5678-90ab-cdef-1234567890ab.json
```

### Step 3: Update Config with Real Tunnel ID

```bash
# Edit the config file
nano ~/.cloudflared/config.yml
```

Replace `<tunnel-id>` with your actual tunnel ID:

**Before:**
```yaml
tunnel: att-mcp
credentials-file: ~/.cloudflared/<tunnel-id>.json
```

**After:**
```yaml
tunnel: att-mcp
credentials-file: ~/.cloudflared/a1b2c3d4-5678-90ab-cdef-1234567890ab.json
```

**Save and exit** (Ctrl+X, then Y, then Enter)

### Step 4: Run the Tunnel

```bash
cloudflared tunnel run att-mcp
```

Should now work! ✅

---

## Alternative: Let Cloudflare Auto-Generate Config

If you want Cloudflare to handle the config:

```bash
# 1. Delete the manual config
rm ~/.cloudflared/config.yml

# 2. Run with inline config
cloudflared tunnel --config /dev/stdin run att-mcp <<EOF
tunnel: att-mcp
credentials-file: /Users/jpaulobr/.cloudflared/$(cloudflared tunnel list | grep att-mcp | awk '{print $1}').json

ingress:
  - service: http://localhost:8000
EOF
```

---

## Easier Option: Use the Tunnel ID Directly

```bash
# Get your tunnel ID
TUNNEL_ID=$(cloudflared tunnel list | grep att-mcp | awk '{print $1}')

# Create config with actual ID
cat > ~/.cloudflared/config.yml <<EOF
tunnel: att-mcp
credentials-file: /Users/jpaulobr/.cloudflared/${TUNNEL_ID}.json

ingress:
  - service: http://localhost:8000
EOF

# Verify config
cat ~/.cloudflared/config.yml

# Run tunnel
cloudflared tunnel run att-mcp
```

---

## Setting Up DNS (Important!)

For a named tunnel to work with a custom domain, you need:

### If you DON'T have a domain:

**Option A: Skip DNS and use the trycloudflare.com URL**

Named tunnels automatically get a trycloudflare.com URL too:

```bash
cloudflared tunnel run att-mcp
```

Look for a line like:
```
https://att-mcp-a1b2c3d4.trycloudflare.com
```

Use this URL! No DNS needed.

### If you HAVE a Cloudflare-managed domain:

```bash
# Route DNS (replace yourdomain.com with your actual domain)
cloudflared tunnel route dns att-mcp att-mcp.yourdomain.com

# Update config with hostname
cat > ~/.cloudflared/config.yml <<EOF
tunnel: att-mcp
credentials-file: /Users/jpaulobr/.cloudflared/$(cloudflared tunnel list | grep att-mcp | awk '{print $1}').json

ingress:
  - hostname: att-mcp.yourdomain.com
    service: http://localhost:8000
  - service: http_status:404
EOF
```

---

## Recommended: Simple Named Tunnel Without Custom Domain

If you don't have a domain, use this simpler approach:

```bash
# 1. Create tunnel (if not already created)
cloudflared tunnel create att-mcp

# 2. Get tunnel ID
TUNNEL_ID=$(cloudflared tunnel list | grep att-mcp | awk '{print $1}')
echo "Tunnel ID: $TUNNEL_ID"

# 3. Create simple config (no hostname needed)
cat > ~/.cloudflared/config.yml <<EOF
tunnel: att-mcp
credentials-file: /Users/jpaulobr/.cloudflared/${TUNNEL_ID}.json

ingress:
  - service: http://localhost:8000
EOF

# 4. Run tunnel
cloudflared tunnel run att-mcp
```

The tunnel will be accessible at:
- `https://att-mcp-<tunnel-id>.trycloudflare.com` (automatically generated)

This URL **never changes** (unlike quick tunnels)!

---

## Update Your .env

Once the tunnel is running, find the URL:

```bash
# Look at the cloudflared output for:
# "Your quick Tunnel has been created! Visit it at:"
# OR
# Check tunnel info
cloudflared tunnel info att-mcp
```

Then update:

```bash
cd att_server_python
nano .env
# Set: SERVER_URL=https://att-mcp-xxxxx.trycloudflare.com
```

Restart Python server:
```bash
python main.py
```

---

## Verify Everything Works

```bash
# Test locally
curl http://localhost:8000/health

# Test through tunnel (replace with your URL)
curl https://att-mcp-xxxxx.trycloudflare.com/health

# Both should return the same JSON
```

---

## Keep Named Tunnel Running

Named tunnels can run as a service:

**macOS:**
```bash
# Install as service
cloudflared service install

# Start
sudo launchctl start com.cloudflare.cloudflared

# Check status
sudo launchctl list | grep cloudflare
```

**Linux:**
```bash
# Install as service
sudo cloudflared service install

# Start
sudo systemctl start cloudflared

# Enable auto-start
sudo systemctl enable cloudflared

# Check status
sudo systemctl status cloudflared
```

This way the tunnel starts automatically on boot!
