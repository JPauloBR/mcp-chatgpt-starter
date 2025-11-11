# AT&T Fiber Coverage Checker Widget

## Overview
A new widget that checks AT&T Fiber and Internet Air availability at a customer's address, featuring an interactive map with coverage heatmaps.

## Implementation Summary

### ✅ Components Created

**1. Widget Directory**: `src/att-fiber-coverage-checker/`

**2. Main Components**:
- **`index.jsx`** - Main orchestrator with conditional rendering logic
- **`AddressForm.jsx`** - Address input form (shown when no address provided)
- **`CoverageMap.jsx`** - Interactive Mapbox map with coverage overlays
- **`AvailabilityResults.jsx`** - Sliding panel showing availability and plans
- **`coverage-data.json`** - Mock coverage zones and address data

### ✅ Key Features

#### **Conditional Entry Points**
The widget handles two scenarios:

1. **Address Pre-Provided** (via ChatGPT conversation)
   - User: "Can I get fiber at 4670 Avocet Dr, Peachtree Corners, GA 30092?"
   - Widget skips input form → Shows map directly with coverage

2. **No Address** (user needs to input)
   - User: "Can I get fiber at my house?"
   - Widget shows address input form
   - On submit, transitions to map view

#### **Coverage Visualization**
- **Blue Zones**: AT&T Fiber coverage (up to 5 Gig speeds)
  - Smaller radius, concentrated in urban areas
  - 30% opacity with blue borders
  
- **Green Zones**: AT&T Internet Air (5G wireless)
  - Larger radius, overlapping Fiber zones
  - 25% opacity with green borders
  
- **Purple Marker**: Customer's house location

#### **Interactive Results Panel**
- Slides in from the right (Framer Motion animations)
- Shows availability status with icons
- Displays available plans with:
  - Speed tiers
  - Pricing (with discounts)
  - Features list
  - Action buttons
- "Help me choose" assistance button

### ✅ MCP Server Integration

**Updated Files**: `att_server_python/main.py`

**Changes**:
1. Added new `ATTWidget` for fiber coverage checker
2. Updated `ATTProductInput` schema to include optional `address` field
3. Updated `TOOL_INPUT_SCHEMA` with address property
4. Modified `_call_tool_request` to pass address via `structuredContent`

**Tool Registration**:
```python
ATTWidget(
    identifier="att-fiber-coverage-checker",
    title="Check Fiber & Internet Air Availability",
    template_uri="ui://widget/att-fiber-coverage-checker.html",
    invoking="Checking AT&T Fiber and Internet Air availability",
    invoked="Coverage checked",
    html=_modify_html_paths(_load_widget_html("att-fiber-coverage-checker")),
    response_text="Displayed AT&T Fiber and Internet Air coverage map...",
)
```

### ✅ Mock Data

**Coverage Zones** (in `coverage-data.json`):
- **Fiber**: 3 zones in SF (Downtown, Mission, SoMa)
- **Internet Air**: 2 larger zones covering Bay Area

**Mock Addresses**: 5 test addresses with different coverage combinations
- Full coverage (Fiber + AIA): Downtown SF, Mission
- AIA only: Haight Street
- All addresses geocoded with coordinates

**Plans**: 5 plan options
- **Fiber**: 5 Gig ($225), 2 Gig ($150), 1 Gig ($55), 500 Mbps ($65)
- **Internet Air**: 5G Wireless ($60)

### ✅ Build Configuration

**Updated**: `build-all.mts`
- Added `"att-fiber-coverage-checker"` to targets array

**Generated Assets**:
- `att-fiber-coverage-checker-2d2b.html`
- `att-fiber-coverage-checker-2d2b.js`
- `att-fiber-coverage-checker-2d2b.css`

## Testing the Widget

### 1. Start the MCP Server

```bash
# Make sure assets are built
pnpm run build

# Start the Python server
cd att_server_python
python main.py
```

Server runs on `http://localhost:8000`

### 2. Expose with ngrok/Cloudflare Tunnel

```bash
ngrok http 8000
# or use your existing Cloudflare tunnel
```

### 3. Add to ChatGPT

1. Enable Developer Mode in ChatGPT
2. Go to Settings > Connectors
3. Add your public URL + `/mcp`
4. Example: `https://your-tunnel.ngrok-free.app/mcp`

### 4. Test Conversations

**With Address**:
```
"Can I get AT&T fiber at 4670 Avocet Dr, Peachtree Corners, GA 30092?"
"Is fiber available at 1 Market St, San Francisco?"
"Check coverage at 2300 Mission St, San Francisco, CA 94110"
```

**Without Address**:
```
"Can I get AT&T fiber at my house?"
"Check fiber availability"
"Show me Internet Air coverage"
```

## Technical Details

### Dependencies
- **mapbox-gl**: Interactive maps with custom overlays
- **framer-motion**: Smooth animations for results panel
- **lucide-react**: Icons (Search, CheckCircle2, X, etc.)
- **react-router-dom**: Not used in this widget (kept simple)

### Widget State Management
- Uses `window.oai.widget.getState()` to receive address from ChatGPT
- Uses `window.oai.widget.setState()` to sync state back
- Manages internal state with React hooks

### Geocoding
- Mock geocoding using predefined addresses in `coverage-data.json`
- Falls back to SF Downtown coordinates if address not found
- Real implementation would use Google Maps/Mapbox Geocoding API

### Coverage Logic
- Simple radius-based circles for demo
- Real implementation would use:
  - Actual coverage polygons from AT&T databases
  - Address validation API
  - Real-time availability checks

## Future Enhancements

1. **Real Geocoding**: Integrate Mapbox/Google Geocoding API
2. **Actual Coverage Data**: Replace mock zones with real AT&T coverage
3. **Address Validation**: Validate address format before submission
4. **Installation Scheduling**: Add "Schedule installation" flow
5. **Comparison Tool**: Side-by-side plan comparison
6. **Speed Test Integration**: Show current speeds vs available speeds
7. **Account Linking**: Check existing AT&T account status

## Files Created/Modified

### New Files
- `src/att-fiber-coverage-checker/index.jsx`
- `src/att-fiber-coverage-checker/AddressForm.jsx`
- `src/att-fiber-coverage-checker/CoverageMap.jsx`
- `src/att-fiber-coverage-checker/AvailabilityResults.jsx`
- `src/att-fiber-coverage-checker/coverage-data.json`
- `assets/att-fiber-coverage-checker*.{html,js,css}`

### Modified Files
- `att_server_python/main.py` - Added new tool and address parameter
- `build-all.mts` - Added to build targets

## Success! 🎉

The AT&T Fiber Coverage Checker is now fully implemented and ready to use in ChatGPT conversations!
