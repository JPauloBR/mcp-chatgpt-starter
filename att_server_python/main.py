"""AT&T Products demo MCP server implemented with the Python FastMCP helper.

The server exposes widget-backed tools that render the AT&T Products UI bundle.
Each handler returns the HTML shell via an MCP resource and echoes the selected
product/service as structured content so the ChatGPT client can hydrate the widget.
The module also wires the handlers into an HTTP/SSE stack so you can run the server
with uvicorn on port 8000."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List

import mcp.types as types
from mcp.server.fastmcp import FastMCP
from mcp.server.auth.settings import AuthSettings
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from dotenv import load_dotenv
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Validate and log SERVER_URL configuration
SERVER_URL = os.environ.get('SERVER_URL', 'http://localhost:8000')
logger.info(f"Server URL configured as: {SERVER_URL}")
if SERVER_URL == 'http://localhost:8000':
    logger.warning(
        "SERVER_URL not set in .env file. Using default: http://localhost:8000. "
        "For production/ngrok, set SERVER_URL=https://your-ngrok-url.ngrok-free.app in .env"
    )

# OAuth Configuration
OAUTH_ENABLED = os.environ.get('OAUTH_ENABLED', 'false').lower() == 'true'
OAUTH_ISSUER_URL = os.environ.get('OAUTH_ISSUER_URL', SERVER_URL)
OAUTH_VALID_SCOPES = os.environ.get('OAUTH_VALID_SCOPES', 'read,write').split(',')
OAUTH_DEFAULT_SCOPES = os.environ.get('OAUTH_DEFAULT_SCOPES', 'read').split(',')

logger.info(f"OAuth enabled: {OAUTH_ENABLED}")
if OAUTH_ENABLED:
    logger.info(f"OAuth issuer URL: {OAUTH_ISSUER_URL}")
    logger.info(f"OAuth valid scopes: {OAUTH_VALID_SCOPES}")
    logger.info(f"OAuth default scopes: {OAUTH_DEFAULT_SCOPES}")


@dataclass(frozen=True)
class ATTWidget:
    identifier: str
    title: str
    template_uri: str
    invoking: str
    invoked: str
    html: str
    response_text: str


ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"


def _load_widget_html(component_name: str) -> str:
    """Load widget HTML from the assets directory with fallback to hashed filenames.
    
    Note: No caching to allow SERVER_URL changes without restart.
    HTML files are small and loaded infrequently (only when widgets are initialized).
    """
    html_path = ASSETS_DIR / f"{component_name}.html"
    if html_path.exists():
        logger.debug(f"Loaded widget HTML: {component_name}.html")
        return html_path.read_text(encoding="utf8")

    fallback_candidates = sorted(ASSETS_DIR.glob(f"{component_name}-*.html"))
    if fallback_candidates:
        selected = fallback_candidates[-1]
        logger.debug(f"Loaded widget HTML with hash: {selected.name}")
        return selected.read_text(encoding="utf8")

    raise FileNotFoundError(
        f'Widget HTML for "{component_name}" not found in {ASSETS_DIR}. '
        "Run `pnpm run build` to generate the assets before starting the server."
    )


def _validate_assets_exist() -> None:
    """Validate that required assets exist at startup."""
    if not ASSETS_DIR.exists():
        logger.error(f"Assets directory not found: {ASSETS_DIR}")
        logger.error("Please run 'pnpm run build' to generate assets before starting the server.")
        raise FileNotFoundError(f"Assets directory not found: {ASSETS_DIR}")
    
    # Check for at least one widget HTML file
    html_files = list(ASSETS_DIR.glob("*.html"))
    if not html_files:
        logger.error(f"No HTML files found in {ASSETS_DIR}")
        logger.error("Please run 'pnpm run build' to generate assets.")
        raise FileNotFoundError(f"No HTML assets found in {ASSETS_DIR}")
    
    logger.info(f"Found {len(html_files)} HTML asset files in {ASSETS_DIR}")


def _modify_html_paths(html: str) -> str:
    """Modify asset paths to use the Python server's /assets endpoint.
    
    This function ensures all asset references (JS, CSS, images) point to the correct
    server URL, whether running locally or via ngrok/production.
    """
    base_url = SERVER_URL.rstrip('/')  # Remove trailing slash
    assets_url = f'{base_url}/assets/'
    
    logger.debug(f"Modifying HTML paths to use assets URL: {assets_url}")
    
    # Check if HTML already has correct absolute URLs
    has_correct_urls = base_url in html and '/assets/' in html
    
    # Track replacements for debugging
    replacements_made = 0
    
    # Replace absolute paths
    if 'src="/' in html or 'href="/' in html:
        html = html.replace('src="/', f'src="{assets_url}')
        html = html.replace('href="/', f'href="{assets_url}')
        replacements_made += 1
    
    # Replace localhost:4444 references (dev server)
    if 'localhost:4444' in html:
        html = html.replace('http://localhost:4444/', assets_url)
        html = html.replace('https://localhost:4444/', assets_url)
        replacements_made += 1
    
    # Replace relative paths
    if 'src="./' in html or 'href="./' in html:
        html = html.replace('src="./', f'src="{assets_url}')
        html = html.replace('href="./', f'href="{assets_url}')
        replacements_made += 1
    
    # Handle edge case: srcset attributes for responsive images
    if 'srcset="' in html:
        # Basic handling - may need enhancement for complex srcset
        html = html.replace('srcset="/', f'srcset="{assets_url}')
        replacements_made += 1
    
    if replacements_made > 0:
        logger.debug(f"Made {replacements_made} types of path replacements")
    elif not has_correct_urls:
        logger.warning("No path replacements made and no absolute URLs found - HTML may be malformed")
    else:
        logger.debug("HTML already contains correct absolute URLs - no replacements needed")
    
    return html

# Validate assets before loading widgets
_validate_assets_exist()

widgets: List[ATTWidget] = [
    ATTWidget(
        identifier="att-store-locator",
        title="Find AT&T Stores & Services",
        template_uri="ui://widget/att-store-locator.html",
        invoking="Locating AT&T stores and services",
        invoked="Found AT&T locations",
        html=_modify_html_paths(_load_widget_html("att-store-finder")),
        response_text="Displayed AT&T store locations with available products and services!",
    ),
    ATTWidget(
        identifier="att-products-carousel",
        title="Browse AT&T Products",
        template_uri="ui://widget/att-products-carousel.html",
        invoking="Loading AT&T products",
        invoked="Products loaded",
        html=_modify_html_paths(_load_widget_html("att-products-carousel")),
        response_text="Displayed AT&T products carousel with cell phones, plans, and accessories!",
    ),
    ATTWidget(
        identifier="att-services-gallery",
        title="View AT&T Services",
        template_uri="ui://widget/att-services-gallery.html",
        invoking="Loading AT&T services",
        invoked="Services loaded",
        html=_modify_html_paths(_load_widget_html("att-products-albums")),
        response_text="Displayed AT&T services including Wireless, Fiber, and Internet Air!",
    ),
    ATTWidget(
        identifier="att-plans-list",
        title="Compare AT&T Plans",
        template_uri="ui://widget/att-plans-list.html",
        invoking="Loading plan options",
        invoked="Plans loaded",
        html=_modify_html_paths(_load_widget_html("att-plans-list")),
        response_text="Displayed AT&T wireless plans with pricing and features!",
    ),
    ATTWidget(
        identifier="att-for-you",
        title="For You - Personalized Recommendations",
        template_uri="ui://widget/att-for-you.html",
        invoking="Loading personalized recommendations",
        invoked="Recommendations loaded",
        html=_modify_html_paths(_load_widget_html("att-for-you")),
        response_text="Displayed personalized AT&T offers and recommendations tailored to your account!",
    ),
    ATTWidget(
        identifier="att-internet-backup-offer",
        title="Internet Backup Offer",
        template_uri="ui://widget/att-internet-backup-offer.html",
        invoking="Loading Internet Backup offer",
        invoked="Offer loaded",
        html=_modify_html_paths(_load_widget_html("att-internet-backup-offer")),
        response_text="Displayed Internet Backup offer - stay connected even during outages!",
    ),
    ATTWidget(
        identifier="att-fiber-coverage-checker",
        title="Check Fiber & Internet Air Availability",
        template_uri="ui://widget/att-fiber-coverage-checker.html",
        invoking="Checking AT&T Fiber and Internet Air availability",
        invoked="Coverage checked",
        html=_modify_html_paths(_load_widget_html("att-fiber-coverage-checker")),
        response_text="Displayed AT&T Fiber and Internet Air coverage map with availability at your location!",
    ),
    ATTWidget(
        identifier="att-make-payment",
        title="Make a Payment",
        template_uri="ui://widget/att-make-payment.html",
        invoking="Opening secure payment interface",
        invoked="Payment interface ready",
        html=_modify_html_paths(_load_widget_html("att-payment")),
        response_text="Opening AT&T payment interface. You can securely enter your account information and payment details in the form below.",
    )
]


MIME_TYPE = "text/html+skybridge"


WIDGETS_BY_ID: Dict[str, ATTWidget] = {widget.identifier: widget for widget in widgets}
WIDGETS_BY_URI: Dict[str, ATTWidget] = {widget.template_uri: widget for widget in widgets}


class ATTProductInput(BaseModel):
    """Schema for AT&T product/service tools."""

    product_type: str = Field(
        ...,
        alias="productType",
        description="Type of AT&T product or service (e.g., 'cell phones', 'wireless plans', 'fiber internet', '5g coverage', 'payment').",
    )
    address: str | None = Field(
        None,
        alias="address",
        description="Customer's address for checking service availability (optional). Include full address with street, city, state, and ZIP code.",
    )

    model_config = ConfigDict(populate_by_name=True, extra="forbid")


# Initialize OAuth provider if enabled
oauth_provider = None
auth_settings = None

if OAUTH_ENABLED:
    from oauth_provider import InMemoryOAuthProvider
    
    oauth_provider = InMemoryOAuthProvider(
        issuer_url=OAUTH_ISSUER_URL,
        valid_scopes=OAUTH_VALID_SCOPES,
        default_scopes=OAUTH_DEFAULT_SCOPES,
        access_token_ttl=3600,  # 1 hour
        refresh_token_ttl=86400,  # 24 hours
        auth_code_ttl=600,  # 10 minutes
    )
    
    auth_settings = AuthSettings(
        issuer_url=OAUTH_ISSUER_URL,
        resource_server_url=f"{OAUTH_ISSUER_URL}/mcp",
        client_registration_options={
            "enabled": True,
            "valid_scopes": OAUTH_VALID_SCOPES,
            "default_scopes": OAUTH_DEFAULT_SCOPES,
        },
        revocation_options={
            "enabled": True,
        },
    )
    
    logger.info("OAuth provider initialized")

mcp = FastMCP(
    name="att-products-python",
    stateless_http=True,
    auth_server_provider=oauth_provider if OAUTH_ENABLED else None,
    auth=auth_settings if OAUTH_ENABLED else None,
)


TOOL_INPUT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "productType": {
            "type": "string",
            "description": "Type of AT&T product or service (e.g., 'cell phones', 'wireless plans', 'fiber internet', '5g coverage').",
        },
        "address": {
            "type": "string",
            "description": "Customer's address for checking service availability (optional). Include full address with street, city, state, and ZIP code.",
        }
    },
    "required": ["productType"],
    "additionalProperties": False,
}

# Separate schema for payment tool - optional context hints only (never ask user for these)
PAYMENT_TOOL_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "paymentFlow": {
            "type": "string",
            "enum": ["authenticated", "guest"],
            "description": "OPTIONAL: Infer from context if user wants authenticated ('logged in', 'my account') or guest payment ('without signing in', 'not logged in'). DO NOT ASK USER - infer from their message or omit if unclear.",
        },
        "serviceType": {
            "type": "string",
            "enum": ["wireless", "internet", "prepaid", "uverse", "directv", "business"],
            "description": "OPTIONAL: Infer service type from context if user mentions 'wireless', 'internet', 'fiber', 'prepaid', etc. DO NOT ASK USER - infer from their message or omit if unclear.",
        }
    },
    "additionalProperties": False,
}


def _resource_description(widget: ATTWidget) -> str:
    return f"{widget.title} widget markup"


def _tool_meta(widget: ATTWidget) -> Dict[str, Any]:
    return {
        "openai/outputTemplate": widget.template_uri,
        "openai/toolInvocation/invoking": widget.invoking,
        "openai/toolInvocation/invoked": widget.invoked,
        "openai/widgetAccessible": True,
        "openai/resultCanProduceWidget": True
    }


def _embedded_widget_resource(widget: ATTWidget) -> types.EmbeddedResource:
    return types.EmbeddedResource(
        type="resource",
        resource=types.TextResourceContents(
            uri=widget.template_uri,
            mimeType=MIME_TYPE,
            text=widget.html,
            title=widget.title,
        ),
    )


@mcp._mcp_server.list_tools()
async def _list_tools() -> List[types.Tool]:
    tools = []
    for widget in widgets:
        # Use specific schema for payment tool
        if widget.identifier == "att-make-payment":
            schema = deepcopy(PAYMENT_TOOL_SCHEMA)
            description = "Open AT&T payment interface. IMPORTANT: Do NOT ask user for account numbers, phone numbers, or ZIP codes - these will be collected securely in the widget. You may optionally infer 'paymentFlow' (authenticated vs guest) and 'serviceType' from the user's message context, but NEVER prompt for these - only include if clearly implied in their request."
        else:
            schema = deepcopy(TOOL_INPUT_SCHEMA)
            description = widget.title
        
        tools.append(
            types.Tool(
                name=widget.identifier,
                title=widget.title,
                description=description,
                inputSchema=schema,
                _meta=_tool_meta(widget),
                # To disable the approval prompt for the tools
                annotations={
                    "destructiveHint": False,
                    "openWorldHint": False,
                    "readOnlyHint": True,
                },
            )
        )
    return tools


@mcp._mcp_server.list_resources()
async def _list_resources() -> List[types.Resource]:
    return [
        types.Resource(
            name=widget.title,
            title=widget.title,
            uri=widget.template_uri,
            description=_resource_description(widget),
            mimeType=MIME_TYPE,
            _meta=_tool_meta(widget),
        )
        for widget in widgets
    ]


@mcp._mcp_server.list_resource_templates()
async def _list_resource_templates() -> List[types.ResourceTemplate]:
    return [
        types.ResourceTemplate(
            name=widget.title,
            title=widget.title,
            uriTemplate=widget.template_uri,
            description=_resource_description(widget),
            mimeType=MIME_TYPE,
            _meta=_tool_meta(widget),
        )
        for widget in widgets
    ]


async def _handle_read_resource(req: types.ReadResourceRequest) -> types.ServerResult:
    widget = WIDGETS_BY_URI.get(str(req.params.uri))
    if widget is None:
        return types.ServerResult(
            types.ReadResourceResult(
                contents=[],
                _meta={"error": f"Unknown resource: {req.params.uri}"},
            )
        )

    contents = [
        types.TextResourceContents(
            uri=widget.template_uri,
            mimeType=MIME_TYPE,
            text=widget.html,
            _meta=_tool_meta(widget),
        )
    ]

    return types.ServerResult(types.ReadResourceResult(contents=contents))


async def _call_tool_request(req: types.CallToolRequest) -> types.ServerResult:
    widget = WIDGETS_BY_ID.get(req.params.name)
    if widget is None:
        return types.ServerResult(
            types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=f"Unknown tool: {req.params.name}",
                    )
                ],
                isError=True,
            )
        )

    arguments = req.params.arguments or {}
    
    logger.info(f"[Tool Debug] Tool called: {req.params.name}")
    logger.info(f"[Tool Debug] Raw arguments: {arguments}")
    
    # Payment tool has optional context parameters (not user input)
    if widget.identifier == "att-make-payment":
        structured_content: Dict[str, Any] = {}
        # Pass optional context hints to widget if provided
        if "paymentFlow" in arguments:
            structured_content["paymentFlow"] = arguments["paymentFlow"]
            logger.info(f"[Tool Debug] Payment flow hint: {arguments['paymentFlow']}")
        if "serviceType" in arguments:
            structured_content["serviceType"] = arguments["serviceType"]
            logger.info(f"[Tool Debug] Service type hint: {arguments['serviceType']}")
    else:
        # Other tools may have productType and address
        try:
            payload = ATTProductInput.model_validate(arguments)
        except ValidationError as exc:
            return types.ServerResult(
                types.CallToolResult(
                    content=[
                        types.TextContent(
                            type="text",
                            text=f"Input validation error: {exc.errors()}",
                        )
                    ],
                    isError=True,
                )
            )

        product_type = payload.product_type
        address = payload.address
        
        logger.info(f"[Tool Debug] Product type: {product_type}")
        logger.info(f"[Tool Debug] Address received: {address}")
        
        structured_content = {"productType": product_type}
        if address:
            structured_content["address"] = address
            logger.info(f"[Tool Debug] Added address to structuredContent: {address}")
    
    widget_resource = _embedded_widget_resource(widget)
    meta: Dict[str, Any] = {
        "openai.com/widget": widget_resource.model_dump(mode="json"),
        "openai/outputTemplate": widget.template_uri,
        "openai/toolInvocation/invoking": widget.invoking,
        "openai/toolInvocation/invoked": widget.invoked,
        "openai/widgetAccessible": True,
        "openai/resultCanProduceWidget": True,
    }

    return types.ServerResult(
        types.CallToolResult(
            content=[
                types.TextContent(
                    type="text",
                    text=widget.response_text,
                )
            ],
            structuredContent=structured_content,
            _meta=meta
        )
    )


mcp._mcp_server.request_handlers[types.CallToolRequest] = _call_tool_request
mcp._mcp_server.request_handlers[types.ReadResourceRequest] = _handle_read_resource


app = mcp.streamable_http_app()

# Add request logging middleware for debugging
@app.middleware("http")
async def log_requests(request, call_next):
    # Log incoming requests to help debug ChatGPT integration
    logger.info(f"Incoming request: {request.method} {request.url.path}")
    logger.debug(f"Headers: {dict(request.headers)}")
    
    response = await call_next(request)
    
    logger.info(f"Response status: {response.status_code}")
    return response

# Add middleware for tunnel compatibility (ngrok, Cloudflare, etc.)
@app.middleware("http")
async def add_tunnel_compatibility_headers(request, call_next):
    response = await call_next(request)
    
    # ngrok compatibility
    response.headers["ngrok-skip-browser-warning"] = "true"
    
    # Cloudflare Tunnel compatibility
    # Add keep-alive and streaming headers
    response.headers["Connection"] = "keep-alive"
    response.headers["X-Accel-Buffering"] = "no"  # Disable buffering
    
    # Handle Cloudflare's specific requirements for SSE
    if "text/event-stream" in response.headers.get("content-type", ""):
        response.headers["Cache-Control"] = "no-cache"
        response.headers["X-Accel-Buffering"] = "no"
    
    # Remove Cloudflare telemetry headers that might trigger security validation
    # Note: These are added by Cloudflare CDN, so this only affects direct server responses
    headers_to_remove = ["report-to", "nel", "cf-ray", "cf-cache-status"]
    for header in headers_to_remove:
        if header in response.headers:
            del response.headers[header]
    
    return response

# Mount the static files directory
app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")

# Add no-cache middleware for development (prevents Cloudflare caching)
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest
from starlette.responses import Response as StarletteResponse

class NoCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: StarletteRequest, call_next):
        response = await call_next(request)
        # Add no-cache headers for all responses
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

app.add_middleware(NoCacheMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
    expose_headers=["*"],  # Allow Cloudflare to expose all headers
)

# Add health check endpoint for tunnel validation
# Note: Using Starlette's add_route (not FastAPI decorator)
from starlette.responses import JSONResponse
from starlette.requests import Request

async def health_check(request: Request):
    """Health check endpoint for monitoring and tunnel validation."""
    return JSONResponse({
        "status": "healthy",
        "service": "att-mcp-server",
        "assets_available": ASSETS_DIR.exists(),
        "widgets_count": len(widgets),
        "server_url": SERVER_URL
    })

app.add_route("/health", health_check, methods=["GET"])

# OAuth-specific endpoints (only if OAuth is enabled)
if OAUTH_ENABLED:
    from starlette.responses import HTMLResponse, RedirectResponse
    from starlette.templating import Jinja2Templates
    from urllib.parse import parse_qs, urlparse
    
    # Initialize template engine
    TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
    templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
    
    async def oauth_authorize_page(request: Request):
        """Display authorization consent page."""
        try:
            # Parse query parameters
            query_params = dict(request.query_params)
            
            client_id = query_params.get("client_id")
            redirect_uri = query_params.get("redirect_uri")
            state = query_params.get("state", "")
            code_challenge = query_params.get("code_challenge")
            scope = query_params.get("scope", " ".join(OAUTH_DEFAULT_SCOPES))
            temp_key = query_params.get("temp_key")
            scopes = scope.split() if scope else OAUTH_DEFAULT_SCOPES
            
            if not client_id or not temp_key:
                return HTMLResponse("<h1>Error: Missing required parameters</h1>", status_code=400)
            
            # Get client info
            client = await oauth_provider.get_client(client_id)
            client_name = client.client_name if client else "Unknown Application"
            
            # Scope descriptions for better UX
            scope_descriptions = {
                "read": "View AT&T products, services, and store locations",
                "write": "Make changes to your account and preferences",
                "payment": "Process payments on your behalf",
                "account": "Access your account information",
            }
            
            logger.info(f"Displaying consent page for client: {client_id}")
            
            return templates.TemplateResponse(
                "authorize.html",
                {
                    "request": request,
                    "client_id": client_id,
                    "client_name": client_name,
                    "redirect_uri": redirect_uri,
                    "state": state,
                    "code_challenge": code_challenge,
                    "temp_key": temp_key,
                    "scopes": scopes,
                    "scopes_str": " ".join(scopes),
                    "scope_descriptions": scope_descriptions,
                    "action_url": "/oauth/authorize/approve",
                }
            )
        except Exception as e:
            logger.error(f"Error in authorization page: {e}", exc_info=True)
            return HTMLResponse(f"<h1>Error: {str(e)}</h1>", status_code=500)
    
    async def oauth_authorize_approve(request: Request):
        """Handle authorization approval/denial."""
        try:
            # Get form data
            form = await request.form()
            temp_key = form.get("temp_key")
            state = form.get("state", "")
            approved = form.get("approved", "true") == "true"
            
            if not temp_key:
                return HTMLResponse("<h1>Error: Missing temp_key</h1>", status_code=400)
            
            logger.info(f"Processing authorization approval: approved={approved}, temp_key={temp_key[:8]}...")
            
            # Complete authorization
            redirect_url = await oauth_provider.complete_authorization(temp_key, approved)
            
            if not redirect_url:
                return HTMLResponse("<h1>Error: Authorization request expired or invalid</h1>", status_code=400)
            
            # Add state parameter if present
            if state and "?" in redirect_url:
                redirect_url += f"&state={state}"
            elif state:
                redirect_url += f"?state={state}"
            
            logger.info(f"Redirecting to: {redirect_url}")
            
            return RedirectResponse(url=redirect_url, status_code=302)
            
        except Exception as e:
            logger.error(f"Error in authorization approval: {e}", exc_info=True)
            return HTMLResponse(f"<h1>Error: {str(e)}</h1>", status_code=500)
    
    async def oauth_stats(request: Request):
        """OAuth statistics endpoint (for debugging)."""
        if oauth_provider:
            stats = oauth_provider.get_stats()
            return JSONResponse({
                "oauth_enabled": True,
                "issuer_url": OAUTH_ISSUER_URL,
                "valid_scopes": OAUTH_VALID_SCOPES,
                "default_scopes": OAUTH_DEFAULT_SCOPES,
                **stats,
            })
        return JSONResponse({"oauth_enabled": False})
    
    # Add OAuth routes
    app.add_route("/oauth/authorize/page", oauth_authorize_page, methods=["GET"])
    app.add_route("/oauth/authorize/approve", oauth_authorize_approve, methods=["POST"])
    app.add_route("/oauth/stats", oauth_stats, methods=["GET"])
    
    logger.info("OAuth endpoints registered: /oauth/authorize/page, /oauth/authorize/approve, /oauth/stats")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000)
