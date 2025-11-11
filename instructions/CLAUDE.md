# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is an Apps SDK Examples Gallery that demonstrates how to build rich UI widgets for ChatGPT using the Model Context Protocol (MCP) and the Apps SDK. The repository contains example React components that are bundled as standalone widgets and served by MCP servers (Python) that expose these widgets as tools to ChatGPT.

## Development Commands

### Install dependencies
```bash
pnpm install
```

### Build all widget components
```bash
pnpm run build
```
This runs `build-all.mts` which:
- Builds each widget entry point in `src/` into standalone bundles
- Produces hashed `.html`, `.js`, and `.css` files in `assets/`
- Creates both hashed and non-hashed versions of HTML files

### Development mode (Vite dev server)
```bash
pnpm run dev
```

### Serve static assets
```bash
pnpm run serve
```
Starts a static file server at `http://localhost:4444` with CORS enabled.

### TypeScript type checking
```bash
pnpm run tsc          # Check all
pnpm run tsc:app      # Check application code
pnpm run tsc:node     # Check node/build scripts
```

### Running MCP servers

**AT&T Products server:**
```bash
# Setup (first time)
python -m venv .venv
source .venv/bin/activate
pip install -r att_server_python/requirements.txt

# Run
uvicorn att_server_python.main:app --port 8000
# Or: cd att_server_python && python main.py
```

**Solar System server:**
```bash
# Uses same .venv as AT&T server
source .venv/bin/activate
pip install -r solar-system_server_python/requirements.txt
uvicorn solar-system_server_python.main:app --port 8000
```

## Architecture

### Widget Build System

The build system (`build-all.mts`) orchestrates bundling of independent React widgets:

1. **Entry point discovery**: Automatically finds all `src/**/index.{tsx,jsx}` files
2. **Per-widget bundling**: Each widget is built as a completely standalone bundle with:
   - All dependencies inlined (React, Three.js, Mapbox, etc.)
   - Global CSS (`src/index.css`) + widget-specific CSS bundled together
   - Single JS file and single CSS file output
3. **Content hashing**: Bundles are versioned using a hash derived from `package.json` version
4. **HTML generation**: Creates HTML shells that load the hashed assets, using `BASE_URL` environment variable (defaults to `http://localhost:4444`)

### MCP Server Pattern (Python)

The Python MCP servers (`att_server_python/main.py`) follow this pattern:

1. **Widget registration**: Each widget is defined with metadata (`ATTWidget` dataclass):
   - `identifier`: Tool name
   - `template_uri`: Widget resource URI (e.g., `ui://widget/att-store-locator.html`)
   - `html`: The complete HTML bundle loaded from `assets/`
   - `invoking/invoked`: Status messages for ChatGPT UI

2. **MCP endpoints implemented**:
   - `list_tools`: Exposes widgets as callable tools with JSON Schema input contracts
   - `list_resources`: Advertises widget HTML as resources
   - `call_tool`: Handles tool invocations, returns structured content + embedded widget resource
   - `read_resource`: Serves widget HTML on demand

3. **Widget delivery**: Tool responses include:
   - Plain text content (for non-Apps SDK clients)
   - `structuredContent`: Parsed data
   - `_meta["openai.com/widget"]`: Embedded resource with HTML
   - `_meta["openai/outputTemplate"]`: Template URI for widget hydration

4. **Asset serving**: Python server mounts `assets/` directory at `/assets` endpoint and modifies HTML paths to point to this endpoint instead of `localhost:4444`

### Apps SDK Integration

Widgets interact with ChatGPT through the `window.openai` global object (see `src/types.ts`):

- **Input/Output**: `toolInput`, `toolOutput` - Tool invocation data
- **State management**: `widgetState`, `setWidgetState` - Persistent widget state
- **Layout**: `displayMode` (pip/inline/fullscreen), `maxHeight`, `safeArea`
- **Theming**: `theme` (light/dark), `userAgent` (device type, capabilities)
- **Actions**: `callTool()`, `sendFollowUpMessage()`, `openExternal()`, `requestDisplayMode()`

**Hooks for accessing context:**
- `useOpenAiGlobal(key)`: Subscribe to specific global property
- `useWidgetProps<T>()`: Get tool output data typed as `T`
- `useWidgetState<T>()`: Manage persistent widget state
- `useDisplayMode()`: Get/set display mode
- `useMaxHeight()`: Get available height for layout

### Widget Examples

Current widgets showcase different UI patterns:

- **att-store-finder**: Interactive Mapbox map with location markers
- **att-products-carousel**: Horizontal scrolling product cards
- **att-products-list**: Vertical list of products with details
- **att-products-albums**: Photo gallery with fullscreen viewer
- **att-for-you**: Personalized recommendations
- **att-internet-backup-offer**: Promotional offer card
- **solar-system**: 3D Three.js solar system visualization
- **todo**: Simple todo list (reference implementation)

## Key Technical Details

### Build Configuration

- **Primary build**: `vite.assets.config.mts` (used by `build-all.mts`)
- **Dev server**: `vite.config.mts` (for local development)
- **Base path**: Assets use `/assets/` base path for MCP server deployment
- **Target**: ES2022
- **Bundling**: Single-file output per widget (`inlineDynamicImports: true`)

### Widget Self-Containment

Each widget bundle is completely standalone:
- No shared chunk splitting (`cssCodeSplit: false`, no `manualChunks`)
- All React code, dependencies, and styles inlined
- Can be hosted independently or served from any URL

### Deployment

For production deployment:
- Set `BASE_URL` environment variable to your server's public URL
- Build system will generate HTML files pointing to that URL
- MCP server should serve assets from a publicly accessible endpoint

### Testing in ChatGPT

1. Enable [developer mode](https://platform.openai.com/docs/guides/developer-mode)
2. Use ngrok to expose local MCP server: `ngrok http 8000`
3. Add connector in ChatGPT Settings > Connectors with URL: `https://<ngrok-id>.ngrok-free.app/mcp`
4. Select connector in conversation "More" options
5. Invoke widgets by asking relevant questions

## Adding New Widgets

1. Create new directory in `src/` with `index.jsx` or `index.tsx`
2. Use Apps SDK hooks to access tool data and ChatGPT context
3. Add widget name to `targets` array in `build-all.mts`
4. Run `pnpm run build`
5. Register widget in your MCP server's `widgets` list with appropriate metadata
