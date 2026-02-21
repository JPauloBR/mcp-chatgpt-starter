#!/bin/bash
# Test script for OAuth persistence

set -e

echo "=================================="
echo "OAuth Persistence Test"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

cd "$(dirname "$0")/att_server_python"

echo "1. Starting server (will create .oauth_data on first run)..."
echo -e "${YELLOW}Press Ctrl+C after you see 'Uvicorn running'${NC}"
echo ""
python3 main.py &
SERVER_PID=$!

# Wait for server to start
sleep 3

echo ""
echo "=================================="
echo "2. Checking if .oauth_data directory was created..."
if [ -d ".oauth_data" ]; then
    echo -e "${GREEN}✓ .oauth_data directory exists${NC}"
    ls -la .oauth_data/
else
    echo -e "${YELLOW}⚠ .oauth_data not yet created (will be created on first client registration)${NC}"
fi

echo ""
echo "=================================="
echo "3. Server is running. Now:"
echo "   - Connect ChatGPT to your server"
echo "   - Complete OAuth authorization"
echo "   - Then come back here and press Enter"
echo "=================================="
read -p "Press Enter after ChatGPT is connected and authorized..."

echo ""
echo "4. Checking OAuth data..."
if [ -f ".oauth_data/clients.json" ]; then
    echo -e "${GREEN}✓ clients.json exists${NC}"
    echo "   Client count: $(cat .oauth_data/clients.json | python3 -c "import sys,json; data=json.load(sys.stdin); print(len(data))")"
else
    echo -e "${YELLOW}⚠ No clients.json yet${NC}"
fi

if [ -f ".oauth_data/refresh_tokens.json" ]; then
    echo -e "${GREEN}✓ refresh_tokens.json exists${NC}"
    echo "   Token count: $(cat .oauth_data/refresh_tokens.json | python3 -c "import sys,json; data=json.load(sys.stdin); print(len(data))")"
else
    echo -e "${YELLOW}⚠ No refresh_tokens.json yet${NC}"
fi

echo ""
echo "=================================="
echo "5. Stopping server..."
kill $SERVER_PID
wait $SERVER_PID 2>/dev/null || true
echo -e "${GREEN}✓ Server stopped${NC}"

sleep 2

echo ""
echo "=================================="
echo "6. Restarting server (should load persisted data)..."
echo -e "${YELLOW}Look for 'Loaded X clients and Y refresh tokens' in the logs${NC}"
echo ""
python3 main.py &
SERVER_PID=$!

sleep 3

echo ""
echo "=================================="
echo "7. Test complete!"
echo ""
echo "Now try using ChatGPT again."
echo "It should reconnect WITHOUT asking for authorization again."
echo ""
echo -e "${GREEN}If ChatGPT works without re-authorization, the fix is successful!${NC}"
echo ""
echo "Press Ctrl+C to stop the server when done testing."
echo "=================================="

wait $SERVER_PID
