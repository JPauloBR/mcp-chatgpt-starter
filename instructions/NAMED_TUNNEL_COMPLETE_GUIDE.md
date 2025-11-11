# Named Tunnel Complete Setup Guide

Your tunnel ID: `e24ead53-de6b-47d9-9726-3a0297f84b2e`
Your tunnel name: `att-mcp`

## Current Status

✅ Tunnel created  
✅ Credentials file exists at: `/Users/jpaulobr/.cloudflared/e24ead53-de6b-47d9-9726-3a0297f84b2e.json`  
❌ No public URL configured yet

## Option 1: Named Tunnel with Public Hostname (Recommended)

This gives you a permanent public URL without needing a custom domain.

### Step 1: Create Config File

```bash
cat > ~/.cloudflared/config.yml <<'EOF'
tunnel: e24ead53-de6b-47d9-9726-3a0297f84b2e
credentials-file: /Users/jpaulobr/.cloudflared/e24ead53-de6b-47d9-9726-3a0297f84b2e.json

ingress:
  - service: http://localhost:8000
EOF
```

### Step 2: Verify Config

```bash
cat ~/.cloudflared/config.yml
```

Should show:
```yaml
tunnel: e24ead53-de6b-47d9-9726-3a0297f84b2e
credentials-file: /Users/jpaulobr/.cloudflared/e24ead53-de6b-47d9-9726-3a0297f84b2e.json

ingress:
  - service: http://localhost:8000
```

### Step 3: Start the Tunnel

```bash
cloudflared tunnel run e24ead53-de6b-47d9-9726-3a0297f84b2e
```

### Step 4: Find Your Public URL

Look at the cloudflared output carefully. You should see something like:

**Option A - Direct URL shown:**
```
INF Your tunnel is now available at: https://e24ead53-de6b-47d9-9726-3a0297f84b2e.cfargotunnel.com
```

**Option B - Connection registered:**
```
INF Connection registered connIndex=0 ip=198.41.200.X location=XXX
```

If you see Option B, your tunnel is running but you need to access it via:
- `https://<tunnel-id>.cfargotunnel.com`
- OR configure a public hostname

### Step 5: Test Access

Try these URLs (replace with what cloudflared shows):

```bash
# Try cfargotunnel.com domain
curl https://e24ead53-de6b-47d9-9726-3a0297f84b2e.cfargotunnel.com/health

# Or check tunnel info
cloudflared tunnel info att-mcp
```

---

## Option 2: Named Tunnel with Public Hostname Feature

If the cfargotunnel.com URL doesn't work, use Cloudflare's public hostname feature:

### Step 1: Install cloudflared with Public Hostname Support

```bash
# Update to latest version
brew upgrade cloudflared
```

### Step 2: Create Tunnel with Public Hostname

```bash
# Delete existing tunnel
cloudflared tunnel delete att-mcp

# Create new tunnel with public hostname
cloudflared tunnel create att-mcp

# Get new tunnel ID
cloudflared tunnel list
```

### Step 3: Route with Public Hostname

```bash
# This creates a public trycloudflare.com URL
cloudflared tunnel route ip add 0.0.0.0/0 att-mcp
```

### Step 4: Update Config

```bash
# Get the new tunnel ID from: cloudflared tunnel list
NEW_TUNNEL_ID=$(cloudflared tunnel list | grep att-mcp | awk '{print $1}')

cat > ~/.cloudflared/config.yml <<EOF
tunnel: ${NEW_TUNNEL_ID}
credentials-file: /Users/jpaulobr/.cloudflared/${NEW_TUNNEL_ID}.json

ingress:
  - service: http://localhost:8000
EOF
```

### Step 5: Run and Get URL

```bash
cloudflared tunnel run att-mcp
```

Look for the public URL in the output.

---

## Option 3: Use Cloudflare Dashboard (Easiest)

### Step 1: Login to Cloudflare Dashboard

```bash
cloudflared tunnel login
```

This opens your browser to authenticate.

### Step 2: Go to Zero Trust Dashboard

Visit: https://one.dash.cloudflare.com/

Navigate to: **Access** → **Tunnels**

### Step 3: Configure Tunnel in Dashboard

1. Find your `att-mcp` tunnel
2. Click **Configure**
3. Under **Public Hostnames**, click **Add a public hostname**
4. For subdomain: enter `att-mcp` (or leave blank for random)
5. For domain: select `trycloudflare.com` from dropdown
6. For service: 
   - Type: `HTTP`
   - URL: `localhost:8000`
7. Click **Save hostname**

This will give you: `https://att-mcp.trycloudflare.com` (or similar)

---

## Option 4: Quick Setup - No Custom Domain Needed

The simplest way to get a persistent public URL:

### Step 1: Update Your Config

```bash
cat > ~/.cloudflared/config.yml <<EOF
tunnel: e24ead53-de6b-47d9-9726-3a0297f84b2e
credentials-file: /Users/jpaulobr/.cloudflared/e24ead53-de6b-47d9-9726-3a0297f84b2e.json

ingress:
  - service: http://localhost:8000
    originRequest:
      noTLSVerify: true
EOF
```

### Step 2: Start with Debug Logging

```bash
cloudflared tunnel --loglevel debug run e24ead53-de6b-47d9-9726-3a0297f84b2e 2>&1 | grep -i "url\|hostname\|public"
```

This will show any public URLs or hostnames assigned to your tunnel.

### Step 3: Alternative - Check Route List

```bash
cloudflared tunnel route dns att-mcp
```

---

## What URL Will Work?

For a named tunnel WITHOUT a custom domain, try these URLs:

```bash
# Format 1: cfargotunnel.com
https://e24ead53-de6b-47d9-9726-3a0297f84b2e.cfargotunnel.com

# Format 2: If you configured a public hostname
https://att-mcp.trycloudflare.com

# Format 3: Check what cloudflared reports
cloudflared tunnel info att-mcp
```

---

## Current Best Practice for Your Setup

Since you want a persistent URL without a custom domain:

### Complete Steps:

```bash
# 1. Ensure config is correct
cat > ~/.cloudflared/config.yml <<'EOF'
tunnel: e24ead53-de6b-47d9-9726-3a0297f84b2e
credentials-file: /Users/jpaulobr/.cloudflared/e24ead53-de6b-47d9-9726-3a0297f84b2e.json

ingress:
  - service: http://localhost:8000
EOF

# 2. Start tunnel in one terminal
cloudflared tunnel run e24ead53-de6b-47d9-9726-3a0297f84b2e

# 3. In another terminal, check what URL is available
# Look at the cloudflared output for any URL
# OR try the cfargotunnel.com format:
curl https://e24ead53-de6b-47d9-9726-3a0297f84b2e.cfargotunnel.com/health

# 4. If cfargotunnel.com doesn't work, check tunnel routes
cloudflared tunnel route ip show-nat
```

---

## Troubleshooting

### If No Public URL Appears

Named tunnels require either:
1. A custom domain with DNS routing
2. Cloudflare Zero Trust public hostname configuration

**Without these, use a quick tunnel instead:**

```bash
cloudflared tunnel --url http://localhost:8000
```

This immediately gives you a public URL.

### Check Tunnel Status

```bash
# List all tunnels
cloudflared tunnel list

# Get tunnel details
cloudflared tunnel info att-mcp

# Check routes
cloudflared tunnel route dns att-mcp
```

---

## My Recommendation

Given your setup, here's what I suggest:

### For Development/Testing:
**Use quick tunnels** - they're simpler:
```bash
cloudflared tunnel --url http://localhost:8000
```

### For Production:
Either:
1. Get a domain and use named tunnels properly
2. Use Cloudflare Zero Trust dashboard to configure public hostname
3. Continue with quick tunnels (they work great)

---

## Next Steps - Tell Me:

1. **Run this and show me the output:**
   ```bash
   cloudflared tunnel run e24ead53-de6b-47d9-9726-3a0297f84b2e
   ```
   Copy the first 20 lines

2. **Try accessing:**
   ```bash
   curl -I https://e24ead53-de6b-47d9-9726-3a0297f84b2e.cfargotunnel.com/health
   ```

3. **Check tunnel info:**
   ```bash
   cloudflared tunnel info att-mcp
   ```

With this information, I can tell you exactly what URL to use!
