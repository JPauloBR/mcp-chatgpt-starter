# AT&T Payment Widget - Testing Guide

## Quick Test URLs

### Local Development
- **Widget Direct:** http://localhost:4444/att-payment.html
- **Static Assets:** http://localhost:4444/
- **MCP Server:** http://localhost:8000/mcp
- **Health Check:** http://localhost:8000/health

## Current Working Features ✅

### 1. Authentication Screen
**What works:**
- AT&T logo and branding
- User ID selection card
- "Add user ID" button
- "Remove user ID" button
- **"Pay without signing in"** button (primary action)

**How to test:**
1. Open http://localhost:4444/att-payment.html
2. Should see AT&T globe logo
3. Click saved user ID → triggers authenticated flow
4. Click "Pay without signing in" → shows service selector

### 2. Service Selector
**What works:**
- 6 service type cards with icons:
  - AT&T Wireless (📶)
  - Internet / Home Phone (📡)
  - AT&T Prepaid (💳)
  - U-verse® (📺)
  - DIRECTV (📺)
  - Business account (💼)
- Hover effects (scale + shadow)
- "Sign in to your account" link

**How to test:**
1. Click "Pay without signing in" from auth screen
2. Should see 6 service cards in a grid
3. Hover over cards → should scale up and show blue border
4. Click any service → navigates to unauthenticated payment (placeholder)

### 3. Confirmation Screen
**What works:**
- Green success checkmark
- Payment details display
- Confirmation number
- Amount and timestamp
- "Make Another Payment" button
- "Return to Account" button (authenticated only)

**How to test:**
Currently shown after simulated payment (placeholder flows)

### 4. Animations
**What works:**
- Smooth fade-in/out between screens
- Card hover animations
- Loading spinner
- Button transitions

### 5. State Management
**What works:**
- Tracks current view (loading → auth → payment → confirmation)
- Maintains payment flow state
- Handles authenticated vs. unauthenticated routing
- Widget state sync with ChatGPT (when integrated)

## Testing Scenarios

### Scenario A: Guest Wireless Payment
```
1. Start at auth screen
2. Click "Pay without signing in"
3. Click "AT&T Wireless" card
4. See placeholder message: "AT&T Wireless Payment - Coming Soon"
5. Click "Back" → returns to service selector
```

### Scenario B: Authenticated User
```
1. Start at auth screen
2. Click user ID card (jpaulo.araras@gmail.com)
3. See placeholder message: "Authenticated Payment Flow - Coming Soon"
4. Click "Sign out" → returns to auth screen
```

### Scenario C: All Services
Test each of the 6 service types:
- ✅ AT&T Wireless → placeholder
- ✅ Internet / Home Phone → placeholder
- ✅ AT&T Prepaid → placeholder
- ✅ U-verse® → placeholder
- ✅ DIRECTV → placeholder
- ✅ Business account → placeholder

## Mock Data Available

### Authenticated Accounts (in payment-data.json)
```javascript
{
  "accountId": "436156947789",
  "type": "wireless",
  "balance": 0.00,
  "paymentMethods": [
    { "brand": "Apple Card", "last4": "4162" }
  ]
}

{
  "accountId": "338086151",
  "type": "internet",
  "balance": 89.99,
  "paymentMethods": []
}
```

### Unauthenticated Lookups
```javascript
"4705959137": {
  "type": "wireless",
  "balance": 125.50,
  "zipCode": "30092"
}

"338086151": {
  "type": "internet",
  "balance": 89.99,
  "zipCode": "30092"
}
```

## Browser DevTools Testing

### Console Output
Look for these log messages:
```
[Payment Widget] Attempt 1/10: Checking for toolInput...
[Payment Widget] window.openai exists: false
[Payment Widget] ❌ Max attempts reached, showing auth screen
[Payment Widget] User chose guest payment
[Payment Widget] Service selected: wireless
```

### React DevTools
If you have React DevTools installed:
1. Inspect component tree
2. Check state values:
   - `currentView`
   - `isAuthenticated`
   - `paymentFlowState`

### Network Tab
- Check that CSS and JS assets load
- No 404 errors
- Assets loaded from http://localhost:4444

## Integration Testing with ChatGPT

### Prerequisites
1. MCP server running on port 8000
2. Connector configured in ChatGPT
3. Using ngrok or Cloudflare tunnel

### Test Prompts
```
1. "I want to make a payment"
   → Should invoke att-make-payment tool
   → Widget loads with auth screen

2. "Pay my wireless bill"
   → Tool called with productType: "payment"
   → Widget shows payment flow

3. "Make a payment without signing in"
   → Tool called with isAuthenticated: false
   → Widget shows service selector

4. "Pay my bill for account 4705959137"
   → Tool called with accountNumber
   → Widget pre-fills account number
```

## Expected Tool Invocation

When ChatGPT calls the tool, you should see:
```python
[Tool Debug] Tool called: att-make-payment
[Tool Debug] Product type: payment
[Tool Debug] Is authenticated: False
[Tool Debug] Account number: None
[Tool Debug] ZIP code: None
```

## Responsive Testing

### Breakpoints to Test
- **Mobile:** 375px - 639px
- **Tablet:** 640px - 1023px
- **Desktop:** 1024px+

### Expected Behavior
- Mobile: Single column, stacked cards
- Tablet: 2-column grid for services
- Desktop: 3-column grid, centered layout

## Accessibility Testing

### Keyboard Navigation
- Tab through interactive elements
- Focus indicators visible (blue outline)
- Enter/Space activates buttons
- Escape closes modals (when implemented)

### Screen Reader
- All buttons have aria-labels
- Form inputs have labels
- State changes announced
- Error messages associated with inputs

## Performance Testing

### Metrics to Check
```bash
# Build size
ls -lh assets/att-payment*

# Load time (Chrome DevTools)
Performance tab → Reload page
- First Contentful Paint: < 1s
- Time to Interactive: < 2s
- Total Bundle Size: Check Network tab
```

## Common Issues & Solutions

### Issue: Widget Not Loading
**Solution:** 
- Check MCP server is running
- Check assets were built: `ls assets/att-payment*`
- Rebuild if needed: `pnpm run build`

### Issue: Styles Missing
**Solution:**
- Ensure Tailwind CSS is loaded
- Check att-payment.css in assets/
- Clear browser cache

### Issue: Console Errors
**Solution:**
- Check for missing imports
- Verify all components exist
- Check browser console for details

### Issue: Transitions Not Working
**Solution:**
- Framer Motion dependency present
- Check AnimatePresence wrapping
- Verify motion.div components

## Next Phase Preview

### Coming in Phase 2
- 🔜 Account selection cards (wireless/internet)
- 🔜 Balance display
- 🔜 Payment amount input
- 🔜 Payment method selector
- 🔜 Date picker for scheduled payments

### Coming in Phase 3
- 🔜 Account info form (CTN/BAN + ZIP)
- 🔜 Balance request via SMS
- 🔜 Credit card form with validation
- 🔜 Bank account form
- 🔜 Payment review screen

## Automated Testing (Future)

### Unit Tests (to implement)
```bash
# Install testing libraries
pnpm add -D vitest @testing-library/react @testing-library/jest-dom

# Run tests
pnpm test
```

### E2E Tests (to implement)
```bash
# Install Playwright
pnpm add -D @playwright/test

# Run E2E tests
pnpm playwright test
```

---

**Last Updated:** November 11, 2025  
**Phase:** 1 (Core Structure)  
**Status:** Ready for Testing ✅
