# Apps SDK Examples Gallery

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

This repository showcases example UI components to be used with the Apps SDK, as well as example MCP servers that expose a collection of components as tools.
It is meant to be used as a starting point and source of inspiration to build your own apps for ChatGPT.

## MCP + Apps SDK overview

The Model Context Protocol (MCP) is an open specification for connecting large language model clients to external tools, data, and user interfaces. An MCP server exposes tools that a model can call during a conversation and returns results according to the tool contracts. Those results can include extra metadata—such as inline HTML—that the Apps SDK uses to render rich UI components (widgets) alongside assistant messages.

Within the Apps SDK, MCP keeps the server, model, and UI in sync. By standardizing the wire format, authentication, and metadata, it lets ChatGPT reason about your connector the same way it reasons about built-in tools. A minimal MCP integration for Apps SDK implements three capabilities:

1. **List tools** – Your server advertises the tools it supports, including their JSON Schema input/output contracts and optional annotations (for example, `readOnlyHint`).
2. **Call tools** – When a model selects a tool, it issues a `call_tool` request with arguments that match the user intent. Your server executes the action and returns structured content the model can parse.
3. **Return widgets** – Alongside structured content, return embedded resources in the response metadata so the Apps SDK can render the interface inline in the Apps SDK client (ChatGPT).

Because the protocol is transport agnostic, you can host the server over Server-Sent Events or streaming HTTP—Apps SDK supports both.

The MCP servers in this demo highlight how each tool can light up widgets by combining structured payloads with `_meta.openai/outputTemplate` metadata returned from the MCP servers.

## Features

✨ **Rich UI Widgets** – Interactive components for AT&T products, services, and store locators  
🔐 **OAuth 2.0 Authentication** – Built-in OAuth provider for secure access control  
🚀 **Production Ready** – Cloudflare tunnel support with persistent domains  
📱 **Responsive Design** – Modern, mobile-friendly UI components  
🛠️ **Developer Friendly** – Easy setup with comprehensive documentation  

## Repository structure

- `src/` – Source for each widget example.
- `assets/` – Generated HTML, JS, and CSS bundles after running the build step.
- `att_server_python/` – Python MCP server that returns the AT&T Products widgets (with OAuth support).
- `solar-system_server_python/` – Python MCP server for the 3D solar system widget.
- `instructions/` – Comprehensive guides for setup, deployment, OAuth, and troubleshooting.
- `build-all.mts` – Vite build orchestrator that produces hashed bundles for every widget entrypoint.

## Technology Stack

This project uses a modern full-stack architecture combining Python backend services with React-based UI widgets.

### Frontend (UI Widgets)

| Technology | Version | Purpose |
|------------|---------|---------|
| **React** | 19.x | Core UI framework for building interactive widgets |
| **TypeScript** | 5.9+ | Type-safe JavaScript for improved developer experience |
| **Vite** | 7.x | Lightning-fast build tool and dev server |
| **TailwindCSS** | 4.x | Utility-first CSS framework for styling |
| **Framer Motion** | 12.x | Animation library for smooth UI transitions |
| **React Three Fiber** | 9.x | React renderer for Three.js (3D solar system widget) |
| **Three.js** | 0.179+ | 3D graphics library |
| **Mapbox GL** | 3.x | Interactive maps for store locator widget |
| **Leaflet** | 1.9+ | Alternative mapping library |
| **Lucide React** | 0.536+ | Icon library |
| **Embla Carousel** | 8.x | Carousel component for product browsing |
| **Zod** | 4.x | Schema validation |
| **React Router** | 7.x | Client-side routing |
| **React Intl** | 7.x | Internationalization support |

### Backend (MCP Server)

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.10+ | Backend runtime |
| **FastAPI** | 0.115+ | High-performance async web framework |
| **FastMCP** | 0.1+ | Model Context Protocol SDK for Python |
| **Uvicorn** | 0.30+ | ASGI server for FastAPI |
| **Pydantic** | 2.x | Data validation using Python type hints |
| **Jinja2** | 3.1+ | HTML templating for OAuth consent pages |
| **HTTPX** | 0.27+ | Async HTTP client |
| **python-dotenv** | 1.0+ | Environment variable management |

### OAuth 2.0 Implementation

The server includes a **custom OAuth 2.0 provider** with support for:

- **Dynamic Client Registration** – ChatGPT auto-registers as an OAuth client
- **Authorization Code Flow with PKCE** – Secure authentication flow
- **Token Management** – Access tokens, refresh tokens, and revocation
- **Persistent Storage** – JSON-based storage for OAuth data (clients, tokens, auth codes)
- **Multiple Provider Support** – Custom, Google OAuth, and Azure Entra ID

### Build & Development Tools

| Tool | Purpose |
|------|---------|
| **pnpm** | Fast, disk-efficient package manager |
| **tsx** | TypeScript execution for build scripts |
| **esbuild** | Fast JavaScript bundler (via Vite) |
| **fast-glob** | File pattern matching for multi-entry builds |
| **serve** | Static file server for previewing built assets |

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         ChatGPT Client                          │
└──────────────────────────────┬──────────────────────────────────┘
                               │ MCP Protocol (HTTP/SSE)
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MCP Server (FastAPI + FastMCP)               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │  Tool Handlers  │  │  OAuth Provider │  │  Static Assets  │  │
│  │  (Widgets)      │  │  (Auth Flow)    │  │  (/assets/)     │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Widget HTML/JS/CSS Bundles                   │
│  (React components compiled with Vite + TailwindCSS)            │
└─────────────────────────────────────────────────────────────────┘
```

### Key Design Patterns

- **Multi-Entry Build System** – Each widget is built as an independent bundle with its own HTML, JS, and CSS
- **Widget Metadata Protocol** – MCP responses include `_meta.openai/outputTemplate` for ChatGPT widget rendering
- **CSP Compliance** – Content Security Policy headers for secure widget embedding in ChatGPT
- **Factory Pattern** – OAuth provider creation via factory for extensibility
- **Persistent Token Storage** – Thread-safe JSON storage with automatic expiration cleanup

## Prerequisites

- Node.js 18+
- pnpm (recommended) or npm/yarn
- Python 3.10+ (for the Python MCP server)

## Install dependencies

Clone the repository and install the workspace dependencies:

```bash
pnpm install
```

> Using npm or yarn? Install the root dependencies with your preferred client and adjust the commands below accordingly.

## Build the components gallery

The components are bundled into standalone assets that the MCP servers serve as reusable UI resources.

```bash
pnpm run build
```

This command runs `build-all.mts`, producing versioned `.html`, `.js`, and `.css` files inside `assets/`. Each widget is wrapped with the CSS it needs so you can host the bundles directly or ship them with your own server.

To iterate on your components locally, you can also launch the Vite dev server:

```bash
pnpm run dev
```

## Serve the static assets

If you want to preview the generated bundles without the MCP servers, start the static file server after running a build:

```bash
pnpm run serve
```

The assets are exposed at [`http://localhost:4444`](http://localhost:4444) with CORS enabled so that local tooling (including MCP inspectors) can fetch them.

## Run the MCP servers

The repository ships several demo MCP servers that highlight different widget bundles:

- **AT&T Products (Python)** – AT&T stores, products, and services locator with interactive map
- **Solar system (Python)** – 3D solar system viewer

Every tool response includes plain text content, structured JSON, and `_meta.openai/outputTemplate` metadata so the Apps SDK can hydrate the matching widget.

### AT&T Products Python server

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r att_server_python/requirements.txt
uvicorn att_server_python.main:app --port 8000
```

Or run directly:

```bash
cd att_server_python
python main.py
```

### Solar system Python server

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r solar-system_server_python/requirements.txt
uvicorn solar-system_server_python.main:app --port 8000
```

You can reuse the same virtual environment for all Python servers—install the dependencies once and run whichever entry point you need.

## Testing in ChatGPT

To add these apps to ChatGPT, enable [developer mode](https://platform.openai.com/docs/guides/developer-mode), and add your apps in Settings > Connectors.

To add your local server without deploying it, you can use a tool like [ngrok](https://ngrok.com/) to expose your local server to the internet.

For example, once your mcp servers are running, you can run:

```bash
ngrok http 8000
```

You will get a public URL that you can use to add your local server to ChatGPT in Settings > Connectors.

For example: `https://<custom_endpoint>.ngrok-free.app/mcp`

Once you add a connector, you can use it in ChatGPT conversations.

You can add your app to the conversation context by selecting it in the "More" options.

![more-chatgpt](https://github.com/user-attachments/assets/26852b36-7f9e-4f48-a515-aebd87173399)

You can then invoke tools by asking something related. For example, for the AT&T Products app, you can ask:

- "Find AT&T stores near me"
- "Show me AT&T wireless plans"
- "What cell phones are available at AT&T?"
- "Where can I get AT&T Fiber internet?"
- "What do you recommend for me?" or "Show me personalized offers"
- "Tell me about Internet Backup" or "Do you have Internet Backup offers?"

## OAuth Authentication (Optional)

The AT&T MCP server includes built-in OAuth 2.0 authentication for secure access control.

### Quick Start

```bash
# 1. Enable OAuth in .env
cd att_server_python
cp .env.example .env
# Edit .env: Set OAUTH_ENABLED=true

# 2. Install dependencies (includes jinja2)
pip install -r requirements.txt

# 3. Start server
python main.py

# 4. Test OAuth
curl https://your-domain.com/oauth/stats | jq
```

### Features

- ✅ **Dynamic Client Registration** – ChatGPT auto-registers as a client
- ✅ **Authorization Code Flow** – Standard OAuth 2.0 with PKCE
- ✅ **Custom Consent UI** – Modern authorization page
- ✅ **Flexible Scopes** – Fine-grained access control
- ✅ **Token Management** – Access tokens, refresh tokens, and revocation

### Documentation

- **[Quick Start Guide](instructions/OAUTH_QUICK_START.md)** – Get OAuth running in 5 minutes
- **[Complete Setup Guide](instructions/OAUTH_SETUP_GUIDE.md)** – Full documentation and troubleshooting
- **[Implementation Summary](OAUTH_IMPLEMENTATION_SUMMARY.md)** – What's been implemented

### Configuration

OAuth is configured via environment variables in `.env`:

```bash
OAUTH_ENABLED=true
OAUTH_ISSUER_URL=https://att-mcp.jpaulo.io
OAUTH_VALID_SCOPES=read,write,payment,account
OAUTH_DEFAULT_SCOPES=read
```

See [OAUTH_SETUP_GUIDE.md](instructions/OAUTH_SETUP_GUIDE.md) for detailed configuration options.

## Next steps

- Customize the widget data: edit the handlers in `att_server_python/main.py` or the solar system server to fetch data from your systems.
- Create your own components and add them to the gallery: drop new entries into `src/` and they will be picked up automatically by the build script.

### Deploy your MCP server

You can use the cloud environment of your choice to deploy your MCP server.

Include this in the environment variables:

```
BASE_URL=https://your-server.com
```

This will be used to generate the HTML for the widgets so that they can serve static assets from this hosted url.

## Contributing

You are welcome to open issues or submit PRs to improve this app, however, please note that we may not review all suggestions.

## License

This project is licensed under the MIT License. See [LICENSE](./LICENSE) for details.
