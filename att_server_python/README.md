# AT&T Products MCP server (Python)

This directory packages a Python implementation of the AT&T Products demo server using the `FastMCP` helper from the official Model Context Protocol SDK. It exposes AT&T product and service widgets as both resources and tools.

## Prerequisites

- Python 3.10+
- A virtual environment (recommended)

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> **Heads up:** There is a similarly named package named `modelcontextprotocol`
> on PyPI that is unrelated to the official MCP SDK. The requirements file
> installs the official `mcp` distribution with its FastAPI extra so that the
> `mcp.server.fastmcp` module is available. If you previously installed the
> other project, run `pip uninstall modelcontextprotocol` before reinstalling
> the requirements.

## Run the server

```bash
python main.py
```

This boots a FastAPI app with uvicorn on `http://127.0.0.1:8000` (equivalently `uvicorn att_server_python.main:app --port 8000`). The endpoints are:

- `GET /mcp` exposes the SSE stream.
- `POST /mcp/messages?sessionId=...` accepts follow-up messages for an active session.

Cross-origin requests are allowed so you can drive the server from local tooling or the MCP Inspector. Each tool returns structured content that includes the requested product type plus metadata that points to the correct widget shell for AT&T stores, products, services, and plans.

## Next steps

Use these handlers as a starting point when wiring in real data, authentication, or localization support. The structure demonstrates how to:

1. Register reusable UI resources that load static HTML bundles.
2. Associate tools with those widgets via `_meta.openai/outputTemplate`.
3. Ship structured JSON alongside human-readable confirmation text.
