# Make a Payment Feature - Quick Start Guide

## 📋 Prerequisites
- Node.js 18+
- pnpm installed
- Python 3.10+ with venv
- Existing project structure in place

## 🚀 Quick Start Steps

### 1. Create Component Directory
```bash
cd /Users/jpaulobr/Projects/mcp-chatgpt-starter/src
mkdir att-payment
cd att-payment
```

### 2. Create Required Files
```bash
touch index.jsx
touch AuthenticationScreen.jsx
touch ServiceSelector.jsx
touch AuthenticatedPayment.jsx
touch UnauthenticatedPayment.jsx
touch AccountSelector.jsx
touch AccountInfoForm.jsx
touch BalanceDisplay.jsx
touch AmountInput.jsx
touch PaymentMethodSelector.jsx
touch PaymentMethodForm.jsx
touch ConfirmationScreen.jsx
touch payment-data.json
```

### 3. Install Additional Dependencies (if needed)
```bash
cd /Users/jpaulobr/Projects/mcp-chatgpt-starter
pnpm add react-input-mask card-validator
```

### 4. Add Widget to MCP Server
Edit `att_server_python/main.py` and add the payment widget to the `widgets` list.

### 5. Build Assets
```bash
pnpm run build
```

### 6. Start Development Server
```bash
# Terminal 1: Frontend dev server
pnpm run dev

# Terminal 2: MCP Python server
cd att_server_python
python main.py
```

## 📝 Implementation Checklist

### Phase 1: Core Structure (Week 1)
- [ ] Create all component files
- [ ] Set up mock data in `payment-data.json`
- [ ] Implement main `index.jsx` with routing logic
- [ ] Add `AuthenticationScreen` component
- [ ] Add `ServiceSelector` component
- [ ] Test basic flow switching

### Phase 2: Authenticated Flow (Week 2)
- [ ] Build `AuthenticatedPayment` container
- [ ] Implement `AccountSelector` (wireless/internet cards)
- [ ] Implement `BalanceDisplay` with mock data
- [ ] Implement `AmountInput` with validation
- [ ] Implement `PaymentMethodSelector`
- [ ] Test authenticated payment flow end-to-end

### Phase 3: Unauthenticated Flow (Week 3)
- [ ] Build `UnauthenticatedPayment` container
- [ ] Implement `AccountInfoForm` (CTN/BAN + ZIP)
- [ ] Add balance request feature (SMS simulation)
- [ ] Implement `PaymentMethodForm` (credit card + bank)
- [ ] Add form validation for all fields
- [ ] Test unauthenticated payment flow end-to-end

### Phase 4: Confirmation & Polish (Week 4)
- [ ] Implement `ConfirmationScreen`
- [ ] Add loading states and spinners
- [ ] Add error handling and error messages
- [ ] Implement animations with Framer Motion
- [ ] Add responsive design breakpoints
- [ ] Test on mobile, tablet, and desktop

### Phase 5: MCP Integration (Week 5)
- [ ] Add payment widget to `main.py`
- [ ] Create tool input schema
- [ ] Implement tool handler
- [ ] Test with ChatGPT connector
- [ ] Handle pre-populated data from ChatGPT
- [ ] Test widget state synchronization

## 🧪 Testing Commands

```bash
# Unit tests (when implemented)
pnpm test

# Build production assets
pnpm run build

# Serve static assets
pnpm run serve

# Check TypeScript
pnpm run tsc
```

## 🔑 Key Files to Reference

### Existing Widget Examples
- `src/att-fiber-coverage-checker/index.jsx` - Multi-step flow
- `src/att-products-carousel/index.jsx` - Card layout
- `src/att-for-you/index.jsx` - Simple widget

### MCP Server
- `att_server_python/main.py` - Widget definitions and tools

### Build Config
- `build-all.mts` - Asset bundling
- `vite.config.mts` - Vite configuration

## 🎯 Success Criteria

### Authenticated Flow
✅ User can select wireless or internet account  
✅ Balance is displayed correctly  
✅ User can enter custom amount  
✅ User can select/change payment method  
✅ Payment confirmation is shown  

### Unauthenticated Flow
✅ User can select service type (6 options)  
✅ User can enter CTN/BAN + ZIP  
✅ User can request balance via SMS  
✅ User can enter credit card or bank details  
✅ Payment confirmation is shown  

### Technical
✅ Widget loads in ChatGPT  
✅ Pre-populated data from ChatGPT works  
✅ State updates to ChatGPT  
✅ Responsive on all screen sizes  
✅ Accessible (keyboard, screen reader)  
✅ No console errors  

## 🐛 Common Issues & Solutions

### Widget Not Loading
- Check `pnpm run build` completed successfully
- Verify assets exist in `/assets` directory
- Check Python server is running on port 8000
- Verify MCP endpoint in ChatGPT settings

### Data Not Pre-filling
- Check `window.openai.toolInput` in browser console
- Verify tool handler in `main.py` returns correct structure
- Add retry logic in component (see fiber-coverage-checker)

### Styling Issues
- Ensure Tailwind classes are correct
- Check for conflicting CSS
- Use browser dev tools to inspect elements
- Reference existing widgets for patterns

## 📞 Next Steps After Implementation

1. **User Testing:** Get feedback from real users
2. **API Integration:** Replace mock data with real payment APIs
3. **Security Audit:** Review payment handling and PCI compliance
4. **Performance:** Optimize bundle size and load times
5. **Analytics:** Add tracking for user flows
6. **Documentation:** Create user guide and API docs

## 📚 Additional Resources

- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [Apps SDK Documentation](https://platform.openai.com/docs/guides/apps)
- [React Documentation](https://react.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Framer Motion](https://www.framer.com/motion/)

---

**Ready to start?** Begin with Phase 1 and work through each checklist item. Refer to `PAYMENT_FEATURE_PLAN.md` for detailed specifications.
