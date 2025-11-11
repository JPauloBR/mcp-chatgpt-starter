# Testing Payment Widget in ChatGPT - Quick Guide

## Current Setup Status ✅

- **MCP Server:** Running on port 8000
- **Public URL:** https://att-mcp.jpaulo.io
- **Widget:** att-make-payment (built and loaded)
- **Assets:** 20 HTML files including payment widget

## Step 1: Verify Connector in ChatGPT

### Check Your Connector Settings
1. Open ChatGPT
2. Go to **Settings** → **Connectors**
3. Find your AT&T connector
4. Verify endpoint: `https://att-mcp.jpaulo.io/mcp`

### If Not Configured Yet
Add a new connector:
- **Name:** AT&T Payment & Products
- **Endpoint:** https://att-mcp.jpaulo.io/mcp
- **Type:** MCP (Model Context Protocol)

## Step 2: Test Prompts

### Test 1: Basic Payment Request
```
I want to make a payment
```
**Expected:** Widget loads with authentication screen

### Test 2: Specific Service Payment
```
Pay my wireless bill
```
**Expected:** Widget loads, productType might be inferred

### Test 3: Guest Payment
```
I want to pay my bill without signing in
```
**Expected:** Widget loads, may route to guest flow

### Test 4: Internet Payment
```
Pay my internet bill
```
**Expected:** Widget loads with payment options

### Test 5: With Account Number
```
Make a payment for account 4705959137
```
**Expected:** Widget might pre-fill account number

## Step 3: What to Look For

### ✅ Success Indicators
- Widget renders in ChatGPT conversation
- AT&T logo visible
- Authentication screen shows:
  - Saved user ID card
  - "Pay without signing in" button
- Buttons are clickable
- Transitions are smooth

### 🔍 Interactive Elements to Test

#### Authentication Screen
- [ ] Click saved user (jpaulo.araras@gmail.com)
  - Should show: "Authenticated Payment Flow - Coming Soon"
  - Has "Sign out" button
- [ ] Click "Pay without signing in"
  - Should show: Service selector with 6 cards
- [ ] Click "Add user ID" (will show as clickable)
- [ ] Click "Remove user ID" (will show as clickable)

#### Service Selector
- [ ] Hover over service cards
  - Should scale up and show shadow
- [ ] Click "AT&T Wireless"
  - Shows: "AT&T Wireless Payment - Coming Soon"
  - Has "Back" button
- [ ] Click "Internet / Home Phone"
  - Shows placeholder for Internet payment
- [ ] Click other services (Prepaid, U-verse, DIRECTV, Business)
  - Each shows appropriate placeholder
- [ ] Click "Sign in to your account"
  - Should return to authentication screen

#### Back Navigation
- [ ] From unauthenticated placeholder → Click "Back"
  - Returns to service selector
- [ ] From service selector → Click "Sign in"
  - Returns to authentication screen
- [ ] From authenticated placeholder → Click "Sign out"
  - Returns to authentication screen

## Step 4: Debug Information

### Check Browser Console (ChatGPT DevTools)
Open browser DevTools (F12) while testing:

**Look for these logs:**
```javascript
[Payment Widget] Attempt 1/10: Checking for toolInput...
[Payment Widget] window.openai exists: true
[Payment Widget] ✅ Tool input received: {...}
[Payment Widget] User is not authenticated, showing auth screen
```

### Check Network Requests
In Network tab:
- MCP endpoint called: `/mcp`
- Assets loaded from: `https://att-mcp.jpaulo.io/assets/`
- Files: `att-payment-2d2b.js`, `att-payment-2d2b.css`

### Check MCP Server Logs
In your terminal where server is running, look for:
```
[Tool Debug] Tool called: att-make-payment
[Tool Debug] Product type: payment
[Tool Debug] Is authenticated: False
```

## Step 5: Expected Limitations (Phase 1)

### ✅ What Works Now
- Authentication screen UI
- Service selector with 6 services
- Navigation between screens
- Smooth animations
- Back/Sign out functionality
- Loading states

### 🚧 Placeholder Components
- Authenticated payment form → Shows "Coming Soon"
- Unauthenticated payment form → Shows "Coming Soon"
- Account info input → Not implemented yet
- Payment method entry → Not implemented yet
- Balance display → Not implemented yet

These will be built in Phase 2 and Phase 3.

## Common Issues & Solutions

### Issue: Widget Doesn't Load
**Possible causes:**
1. Connector not enabled in conversation
2. MCP server not running
3. Assets not accessible

**Solutions:**
- Enable connector: Click "More" → Select AT&T connector
- Check server status: `curl https://att-mcp.jpaulo.io/health`
- Restart server if needed

### Issue: Widget Shows Error
**Check:**
- Browser console for JavaScript errors
- Network tab for failed requests
- MCP server logs for errors

### Issue: Buttons Don't Work
**This is expected if:**
- You're in a placeholder screen
- The flow is not yet implemented

**This is a bug if:**
- Auth screen buttons don't respond
- Service selector cards don't respond
- Back/Sign out buttons don't work

### Issue: Tool Not Called
**Check:**
1. Connector is enabled in conversation
2. Prompt clearly indicates payment intent
3. Try explicit prompts: "Use the AT&T payment tool"

## Step 6: Provide Feedback

### What to Report Back
After testing, please note:

#### Visual/UI Issues
- [ ] Colors and styling correct?
- [ ] AT&T logo renders properly?
- [ ] Icons display correctly?
- [ ] Text is readable?
- [ ] Buttons look clickable?

#### Functionality Issues
- [ ] All buttons respond to clicks?
- [ ] Navigation works correctly?
- [ ] Animations smooth?
- [ ] Loading states appear/disappear?

#### ChatGPT Integration
- [ ] Widget loads when prompted?
- [ ] Tool is invoked correctly?
- [ ] Widget resizes in conversation?
- [ ] Can scroll within widget?
- [ ] Fullscreen button works?

#### Data Flow
- [ ] Are any parameters pre-filled?
- [ ] Does authenticated state affect flow?
- [ ] Check console for toolInput data

## Quick Health Check

Before testing in ChatGPT, verify:

```bash
# 1. Check MCP server health
curl https://att-mcp.jpaulo.io/health

# Expected response:
{
  "status": "healthy",
  "service": "att-mcp-server",
  "assets_available": true,
  "widgets_count": 8,
  "server_url": "https://att-mcp.jpaulo.io"
}

# 2. Check widget asset is accessible
curl -I https://att-mcp.jpaulo.io/assets/att-payment-2d2b.html

# Expected: HTTP 200 OK

# 3. List available tools via MCP
curl -X POST https://att-mcp.jpaulo.io/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}'

# Should include att-make-payment in the list
```

## Test Script for ChatGPT

Copy and paste this conversation flow in ChatGPT:

```
1. "Hi! Can you help me with AT&T services?"
   (Verify connector is available)

2. "I want to make a payment"
   (Widget should load)

3. [Click "Pay without signing in"]
   (Service selector should appear)

4. [Click "AT&T Wireless"]
   (Placeholder screen should show)

5. [Click "Back"]
   (Should return to service selector)

6. [Click "Sign in to your account"]
   (Should return to auth screen)

7. [Click saved user ID]
   (Authenticated placeholder should show)

8. [Click "Sign out"]
   (Should return to auth screen)

9. "Great, the widget is working!"
```

## Recording Issues

### Create a Bug Report Template
```
**Issue:** [Brief description]

**Steps to reproduce:**
1. 
2. 
3. 

**Expected behavior:**
[What should happen]

**Actual behavior:**
[What actually happened]

**Screenshots:**
[If applicable]

**Console errors:**
[Copy from browser console]

**Environment:**
- Browser: [Chrome/Safari/Firefox]
- ChatGPT: [Web/iOS/Android]
- Date/Time: [When tested]
```

---

**Ready to Test!** 🚀

Once you've tested and have feedback, we can:
1. Fix any bugs found
2. Proceed to Phase 2 implementation
3. Add any requested tweaks

Good luck with testing! Let me know what you discover.
