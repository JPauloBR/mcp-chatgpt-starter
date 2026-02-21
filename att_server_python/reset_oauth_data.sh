#!/bin/bash
# Reset OAuth data to force fresh client registration

set -e

echo "=================================================="
echo "OAuth Data Reset Script"
echo "=================================================="
echo ""

cd "$(dirname "$0")"

# Check if .oauth_data exists
if [ ! -d ".oauth_data" ]; then
    echo "✓ No .oauth_data directory found (nothing to reset)"
    exit 0
fi

echo "Current OAuth data:"
echo ""

if [ -f ".oauth_data/clients.json" ]; then
    echo "Clients:"
    cat .oauth_data/clients.json | python3 -m json.tool | grep -E "(client_id|client_name)" | head -10
    echo ""
fi

if [ -f ".oauth_data/refresh_tokens.json" ]; then
    echo "Refresh tokens:"
    python3 -c "
import json
with open('.oauth_data/refresh_tokens.json', 'r') as f:
    data = json.load(f)
    print(f'  Count: {len(data)}')
    for token_val, token_data in list(data.items())[:2]:
        print(f'  - Client: {token_data.get(\"client_id\")}')
        print(f'    Scopes: {token_data.get(\"scopes\")}')
" 2>/dev/null || echo "  (unable to parse)"
    echo ""
fi

echo ""
echo "=================================================="
read -p "Do you want to BACKUP and DELETE OAuth data? (y/N) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "Creating backup..."
BACKUP_DIR=".oauth_data.backup.$(date +%Y%m%d_%H%M%S)"
cp -r .oauth_data "$BACKUP_DIR"
echo "✓ Backup created: $BACKUP_DIR"

echo ""
echo "Deleting OAuth data..."
rm -rf .oauth_data
echo "✓ OAuth data deleted"

echo ""
echo "=================================================="
echo "✅ OAuth data reset complete!"
echo ""
echo "Next steps:"
echo "  1. Restart your server: python3 main.py"
echo "  2. In ChatGPT settings, REMOVE the AT&T MCP connection"
echo "  3. Add it again - it will re-register with fresh data"
echo ""
echo "The new registration will use the fixed persistence code."
echo "=================================================="
