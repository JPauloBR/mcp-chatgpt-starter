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
from mcp.server.auth.settings import AuthSettings, ClientRegistrationOptions, RevocationOptions
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
OAUTH_PROVIDER = os.environ.get('OAUTH_PROVIDER', 'custom')  # custom, google, azure
OAUTH_ISSUER_URL = os.environ.get('OAUTH_ISSUER_URL', SERVER_URL)
OAUTH_VALID_SCOPES = os.environ.get('OAUTH_VALID_SCOPES', 'read,write,payment,account').split(',')
OAUTH_DEFAULT_SCOPES = os.environ.get('OAUTH_DEFAULT_SCOPES', 'read').split(',')

# Provider-specific credentials (for Google/Azure)
OAUTH_CLIENT_ID = os.environ.get('OAUTH_CLIENT_ID')  # Google/Azure app client ID
OAUTH_CLIENT_SECRET = os.environ.get('OAUTH_CLIENT_SECRET')  # Google/Azure app client secret
OAUTH_TENANT_ID = os.environ.get('OAUTH_TENANT_ID', 'common')  # Azure tenant ID

# Token lifetimes (seconds)
OAUTH_ACCESS_TOKEN_TTL = int(os.environ.get('OAUTH_ACCESS_TOKEN_TTL', '3600'))  # 1 hour
OAUTH_REFRESH_TOKEN_TTL = int(os.environ.get('OAUTH_REFRESH_TOKEN_TTL', '86400'))  # 24 hours
OAUTH_AUTH_CODE_TTL = int(os.environ.get('OAUTH_AUTH_CODE_TTL', '600'))  # 10 minutes

logger.info(f"OAuth enabled: {OAUTH_ENABLED}")
if OAUTH_ENABLED:
    logger.info(f"OAuth provider: {OAUTH_PROVIDER}")
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


def _get_widget_domain() -> str:
    """Extract domain from SERVER_URL for widget metadata."""
    from urllib.parse import urlparse
    parsed = urlparse(SERVER_URL)
    return parsed.netloc or "localhost:8000"


def _get_widget_csp() -> Dict[str, Any]:
    """Generate Content Security Policy object for widgets.
    
    Per OpenAI docs, CSP must be an object with domain arrays:
    - connect_domains: hosts the widget can fetch from
    - resource_domains: hosts for static assets (images, fonts, scripts)
    - redirect_domains: hosts allowed for openExternal redirects
    - frame_domains: hosts the widget may embed as iframes (discouraged)
    """
    scheme = "https" if "https" in SERVER_URL else "http"
    domain = _get_widget_domain()
    origin = f"{scheme}://{domain}"
    
    # Mapbox GL JS requires these domains for map rendering
    mapbox_connect = [
        "https://api.mapbox.com",
        "https://events.mapbox.com",
        "https://*.tiles.mapbox.com",
        "https://a.tiles.mapbox.com",
        "https://b.tiles.mapbox.com",
        "https://c.tiles.mapbox.com",
        "https://d.tiles.mapbox.com",
    ]
    
    mapbox_resources = [
        "https://api.mapbox.com",
        "https://*.tiles.mapbox.com",
        "https://a.tiles.mapbox.com",
        "https://b.tiles.mapbox.com",
        "https://c.tiles.mapbox.com",
        "https://d.tiles.mapbox.com",
    ]
    
    return {
        "connect_domains": [origin] + mapbox_connect,
        "resource_domains": [origin, "https://*.oaistatic.com", "https://images.unsplash.com"] + mapbox_resources,
    }


def _get_widget_csp_string() -> str:
    """Generate CSP string for HTML meta tag (browser enforcement)."""
    scheme = "https" if "https" in SERVER_URL else "http"
    domain = _get_widget_domain()
    origin = f"{scheme}://{domain}"
    
    # Mapbox domains for CSP string
    mapbox_domains = "https://api.mapbox.com https://events.mapbox.com https://*.tiles.mapbox.com"
    
    csp_directives = [
        "default-src 'self'",
        f"script-src 'self' 'unsafe-inline' 'unsafe-eval' {origin} blob:",
        f"style-src 'self' 'unsafe-inline' {origin}",
        f"img-src 'self' data: blob: {origin} https://images.unsplash.com {mapbox_domains}",
        f"font-src 'self' data: {origin}",
        f"connect-src 'self' {origin} https: {mapbox_domains}",
        "worker-src 'self' blob:",
        "child-src 'self' blob:",
        "frame-ancestors 'self' https://chatgpt.com https://*.openai.com",
        "base-uri 'self'",
        "form-action 'self'",
    ]
    return "; ".join(csp_directives)


def _inject_csp_meta_tag(html: str) -> str:
    """Inject CSP meta tag into HTML head for ChatGPT widget compliance."""
    csp = _get_widget_csp_string()
    csp_meta = f'<meta http-equiv="Content-Security-Policy" content="{csp}">'
    
    # Insert CSP meta tag after <head>
    if '<head>' in html:
        html = html.replace('<head>', f'<head>\n{csp_meta}', 1)
    elif '<head ' in html:
        # Handle <head with attributes
        head_end = html.find('>', html.find('<head ')) + 1
        html = html[:head_end] + f'\n{csp_meta}' + html[head_end:]
    
    return html


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
    
    # Replace /assets absolute paths (avoid producing /assets/assets/...)
    if 'src="/assets/' in html or 'href="/assets/' in html or 'srcset="/assets/' in html:
        html = html.replace('src="/assets/', f'src="{assets_url}')
        html = html.replace('href="/assets/', f'href="{assets_url}')
        html = html.replace('srcset="/assets/', f'srcset="{assets_url}')
        replacements_made += 1
    
    # Replace localhost:4444 references (dev server)
    # Only rewrite the /assets/ prefix to avoid duplicating assets in the final URL.
    if 'localhost:4444' in html:
        html = html.replace('http://localhost:4444/assets/', assets_url)
        html = html.replace('https://localhost:4444/assets/', assets_url)
        replacements_made += 1
    
    # Replace relative paths (handle ./assets/ first to avoid /assets/assets/...)
    if 'src="./assets/' in html or 'href="./assets/' in html:
        html = html.replace('src="./assets/', f'src="{assets_url}')
        html = html.replace('href="./assets/', f'href="{assets_url}')
        replacements_made += 1
    if 'src="./' in html or 'href="./' in html:
        html = html.replace('src="./', f'src="{assets_url}')
        html = html.replace('href="./', f'href="{assets_url}')
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
        html=_inject_csp_meta_tag(_modify_html_paths(_load_widget_html("att-store-finder"))),
        response_text="Displayed AT&T store locations with available products and services!",
    ),
    ATTWidget(
        identifier="att-device-details",
        title="Shop Specific Device Model",
        template_uri="ui://widget/att-device-details.html",
        invoking="Loading device details",
        invoked="Device details loaded",
        html=_inject_csp_meta_tag(_modify_html_paths(_load_widget_html("att-device-details"))),
        response_text="Here are the details for the device you selected.",
    ),
    ATTWidget(
        identifier="att-products-carousel",
        title="Browse AT&T Products",
        template_uri="ui://widget/att-products-carousel.html",
        invoking="Loading AT&T products",
        invoked="Products loaded",
        html=_inject_csp_meta_tag(_modify_html_paths(_load_widget_html("att-products-carousel"))),
        response_text="Displayed AT&T products carousel with cell phones, plans, and accessories!",
    ),
    ATTWidget(
        identifier="att-services-gallery",
        title="View AT&T Services",
        template_uri="ui://widget/att-services-gallery.html",
        invoking="Loading AT&T services",
        invoked="Services loaded",
        html=_inject_csp_meta_tag(_modify_html_paths(_load_widget_html("att-products-albums"))),
        response_text="Displayed AT&T services including Wireless, Fiber, and Internet Air!",
    ),
    ATTWidget(
        identifier="att-plans-list",
        title="Compare AT&T Plans",
        template_uri="ui://widget/att-plans-list.html",
        invoking="Loading plan options",
        invoked="Plans loaded",
        html=_inject_csp_meta_tag(_modify_html_paths(_load_widget_html("att-plans-list"))),
        response_text="Displayed AT&T wireless plans with pricing and features!",
    ),
    ATTWidget(
        identifier="att-for-you",
        title="For You - Personalized Recommendations",
        template_uri="ui://widget/att-for-you.html",
        invoking="Loading personalized recommendations",
        invoked="Recommendations loaded",
        html=_inject_csp_meta_tag(_modify_html_paths(_load_widget_html("att-for-you"))),
        response_text="Displayed personalized AT&T offers and recommendations tailored to your account!",
    ),
    ATTWidget(
        identifier="att-internet-backup-offer",
        title="Internet Backup Offer",
        template_uri="ui://widget/att-internet-backup-offer.html",
        invoking="Loading Internet Backup offer",
        invoked="Offer loaded",
        html=_inject_csp_meta_tag(_modify_html_paths(_load_widget_html("att-internet-backup-offer"))),
        response_text="Displayed Internet Backup offer - stay connected even during outages!",
    ),
    ATTWidget(
        identifier="att-fiber-coverage-checker",
        title="Check Fiber & Internet Air Availability",
        template_uri="ui://widget/att-fiber-coverage-checker.html",
        invoking="Checking AT&T Fiber and Internet Air availability",
        invoked="Coverage checked",
        html=_inject_csp_meta_tag(_modify_html_paths(_load_widget_html("att-fiber-coverage-checker"))),
        response_text="Displayed AT&T Fiber and Internet Air coverage map with availability at your location!",
    ),
    ATTWidget(
        identifier="att-make-payment",
        title="Make a Payment",
        template_uri="ui://widget/att-make-payment.html",
        invoking="Opening secure payment interface",
        invoked="Payment interface ready",
        html=_inject_csp_meta_tag(_modify_html_paths(_load_widget_html("att-payment"))),
        response_text="Opening AT&T payment interface. You can securely enter your account information and payment details in the form below.",
    ),
]



MIME_TYPE = "text/html+skybridge"


# Mock data to mirror frontend availability logic (from coverage-data.json)
MOCK_COVERAGE_DATA = [
    {
        "address": "4670 Avocet Dr, Peachtree Corners, GA 30092",
        "fiber": True,
        "internetAir": True
    },
    {
        "address": "1 Market St, San Francisco, CA 94105",
        "fiber": True,
        "internetAir": True
    },
    {
        "address": "2300 Mission St, San Francisco, CA 94110",
        "fiber": True,
        "internetAir": True
    },
    {
        "address": "1700 Haight St, San Francisco, CA 94117",
        "fiber": False,
        "internetAir": True
    },
    {
        "address": "555 California St, San Francisco, CA 94104",
        "fiber": True,
        "internetAir": True
    }
]


def _check_availability(address: str | None) -> dict:
    """Mirror frontend availability logic to provide accurate context to LLM."""
    if not address:
        # Default fallback (matches frontend default)
        return {"fiber": True, "internetAir": True}
        
    addr_lower = address.lower()
    
    # Check mock data
    for mock in MOCK_COVERAGE_DATA:
        mock_addr = mock["address"].lower()
        if mock_addr in addr_lower or addr_lower in mock_addr:
            return {"fiber": mock["fiber"], "internetAir": mock["internetAir"]}
            
    # Default fallback if not found (matches frontend default)
    return {"fiber": True, "internetAir": True}


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
    from oauth_providers.factory import create_provider_from_env, validate_provider_config
    
    # Validate provider configuration
    is_valid, error_msg = validate_provider_config(
        OAUTH_PROVIDER,
        OAUTH_CLIENT_ID,
        OAUTH_CLIENT_SECRET
    )
    
    if not is_valid:
        logger.error(f"OAuth configuration error: {error_msg}")
        logger.error("OAuth will be disabled. Please check your .env file.")
        OAUTH_ENABLED = False
    else:
        # Create OAuth provider
        oauth_provider = create_provider_from_env(
            provider_type=OAUTH_PROVIDER,
            issuer_url=OAUTH_ISSUER_URL,
            client_id=OAUTH_CLIENT_ID,
            client_secret=OAUTH_CLIENT_SECRET,
            tenant_id=OAUTH_TENANT_ID,
            valid_scopes=OAUTH_VALID_SCOPES,
            default_scopes=OAUTH_DEFAULT_SCOPES,
            access_token_ttl=OAUTH_ACCESS_TOKEN_TTL,
            refresh_token_ttl=OAUTH_REFRESH_TOKEN_TTL,
            auth_code_ttl=OAUTH_AUTH_CODE_TTL,
        )
        
        logger.info(f"OAuth provider initialized: {OAUTH_PROVIDER}")
        
        # Configure AuthSettings for MCP
        # The resource_server_url should include the /mcp path where the MCP server is mounted
        resource_server_url = f"{OAUTH_ISSUER_URL.rstrip('/')}/mcp"
        
        auth_settings = AuthSettings(
            issuer_url=OAUTH_ISSUER_URL,
            resource_server_url=resource_server_url,  # MCP server URL with /mcp path
            required_scopes=OAUTH_DEFAULT_SCOPES,
            client_registration_options=ClientRegistrationOptions(
                enabled=True,
                valid_scopes=OAUTH_VALID_SCOPES,
                default_scopes=OAUTH_DEFAULT_SCOPES,
            ),
            revocation_options=RevocationOptions(enabled=True),
        )
        
        logger.info(f"AuthSettings configured: {auth_settings}")

MCP_INSTRUCTIONS = """
AT&T Assistant Tool Selection Rules:

CRITICAL RULE FOR DEVICE REQUESTS:
When a user mentions a SPECIFIC device model name (iPhone 17, iPhone 17 Pro, iPhone 17 Pro Max, Galaxy S25, S25 Ultra, etc.), 
you MUST use the "att-device-details" tool - NOT "att-products-carousel".

Examples that MUST use att-device-details:
- "I'd like to shop for the iPhone 17 Pro Max" → att-device-details with deviceId="iphone-17-pro-max"
- "Show me the new iPhone 17 Pro" → att-device-details with deviceId="iphone-17-pro"
- "I want to buy a Samsung Galaxy S25 Ultra" → att-device-details with deviceId="samsung-s25-ultra"
- "Tell me about ATT's newest iPhone 17 Pro Max" → att-device-details with deviceId="iphone-17-pro-max"

Examples that use att-products-carousel:
- "Show me your phones" → att-products-carousel
- "What devices do you have?" → att-products-carousel
- "Browse cell phones" → att-products-carousel

Device ID format: lowercase with hyphens (e.g., "iphone-17-pro-max", "samsung-s25-ultra")
"""

mcp = FastMCP(
    name="att-products-python",
    instructions=MCP_INSTRUCTIONS,
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


# Device name to ID mapping for LLM inference
DEVICE_NAME_MAPPING: Dict[str, str] = {
    "iphone 17 pro max": "iphone-17-pro-max",
    "iphone17 pro max": "iphone-17-pro-max",
    "iphone 17 promax": "iphone-17-pro-max",
    "iphone 17pro max": "iphone-17-pro-max",
    "iphone 17 pro": "iphone-17-pro",
    "galaxy s25 ultra": "samsung-s25-ultra",
    "samsung s25 ultra": "samsung-s25-ultra",
    "samsung galaxy s25 ultra": "samsung-s25-ultra",
    "s25 ultra": "samsung-s25-ultra",
    "galaxy s25+": "samsung-s25-plus",
    "galaxy s25 plus": "samsung-s25-plus",
    "samsung s25+": "samsung-s25-plus",
    "galaxy s25": "samsung-s25",
    "samsung s25": "samsung-s25",
}

DEVICE_DETAILS_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "deviceId": {
            "type": "string",
            "description": "The device ID to show details for. Convert device names to IDs: 'iPhone 17 Pro Max' -> 'iphone-17-pro-max', 'iPhone 17 Pro' -> 'iphone-17-pro', 'Samsung Galaxy S25 Ultra' -> 'samsung-s25-ultra', 'Galaxy S25+' -> 'samsung-s25-plus', 'Galaxy S25' -> 'samsung-s25'. Use lowercase with hyphens.",
        }
    },
    "required": ["deviceId"],
    "additionalProperties": False,
}


def _resource_description(widget: ATTWidget) -> str:
    return f"{widget.title} widget markup"


def _tool_meta(widget: ATTWidget) -> Dict[str, Any]:
    csp = _get_widget_csp()
    # Domain must be full URL with scheme per OpenAI docs
    scheme = "https" if "https" in SERVER_URL else "http"
    domain = f"{scheme}://{_get_widget_domain()}"
    return {
        "openai/outputTemplate": widget.template_uri,
        "openai/toolInvocation/invoking": widget.invoking,
        "openai/toolInvocation/invoked": widget.invoked,
        "openai/widgetAccessible": True,
        "openai/resultCanProduceWidget": True,
        # Per OpenAI docs: widgetDomain is full URL, widgetCSP is object with domain arrays
        "openai/widgetDomain": domain,
        "openai/widgetCSP": csp,
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
        elif widget.identifier == "att-device-details":
            schema = deepcopy(DEVICE_DETAILS_SCHEMA)
            description = "PRIORITY: Use this tool FIRST when user mentions ANY specific device model name like 'iPhone 17', 'iPhone 17 Pro', 'iPhone 17 Pro Max', 'Galaxy S25', 'S25 Ultra', etc. Triggers: 'shop for iPhone 17 Pro Max', 'buy Samsung S25', 'want the new iPhone', 'interested in iPhone 17', 'newest iPhone 17 Pro Max'. Shows device details with pricing, specs, colors, and trade-in offers. This tool takes priority over att-products-carousel when a specific model is mentioned."
        elif widget.identifier == "att-products-carousel":
            schema = deepcopy(TOOL_INPUT_SCHEMA)
            description = "Browse AT&T products by category ONLY when NO specific model is mentioned. Use for: 'show me phones', 'what phones do you have', 'browse accessories'. NEVER use when user mentions a specific model name (iPhone 17, Galaxy S25, etc.) - those requests MUST use att-device-details instead."
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
    elif widget.identifier == "att-device-details":
        structured_content: Dict[str, Any] = {}
        if "deviceId" in arguments:
            structured_content["deviceId"] = arguments["deviceId"]
            logger.info(f"[Tool Debug] Device ID: {arguments['deviceId']}")
        
        widget_response = widget.response_text
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
            
        # For coverage checker, verify availability to give accurate text response
        if widget.identifier == "att-fiber-coverage-checker":
            availability = _check_availability(address)
            structured_content["availability"] = availability
            
            fiber_avail = availability["fiber"]
            air_avail = availability["internetAir"]
            
            if fiber_avail and air_avail:
                widget_response = f"Great news! Both AT&T Fiber and Internet Air are available at {address or 'your location'}."
            elif fiber_avail:
                widget_response = f"Great news! AT&T Fiber is available at {address or 'your location'}."
            elif air_avail:
                widget_response = f"AT&T Internet Air is available at {address or 'your location'}. AT&T Fiber is not currently available."
            else:
                widget_response = f"Neither AT&T Fiber nor Internet Air is currently available at {address or 'your location'}."
                
            # Override the static response text with the dynamic one
            logger.info(f"[Tool Debug] Generated dynamic response: {widget_response}")
        else:
            widget_response = widget.response_text
    
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
                    text=widget_response,
                )
            ],
            structuredContent=structured_content,
            _meta=meta
        )
    )


mcp._mcp_server.request_handlers[types.CallToolRequest] = _call_tool_request
mcp._mcp_server.request_handlers[types.ReadResourceRequest] = _handle_read_resource


app = mcp.streamable_http_app()

# Initialize OAuth provider on startup
@app.on_event("startup")
async def startup_event():
    """Initialize OAuth provider when the server starts."""
    if OAUTH_ENABLED and oauth_provider:
        logger.info("Initializing OAuth provider...")
        await oauth_provider.initialize()
        logger.info("OAuth provider initialization complete")

# Add request logging middleware for debugging
@app.middleware("http")
async def log_requests(request, call_next):
    # Log incoming requests to help debug ChatGPT integration
    query_string = f"?{request.url.query}" if request.url.query else ""
    logger.info(f"Incoming request: {request.method} {request.url.path}{query_string}")
    logger.debug(f"Headers: {dict(request.headers)}")
    
    # Log request body for OAuth endpoints (debugging)
    if request.url.path in ["/token", "/register"] and request.method == "POST":
        body = await request.body()
        logger.info(f"{request.url.path} request body: {body.decode('utf-8', errors='ignore')}")
        # Recreate request with body for downstream processing
        from starlette.requests import Request as StarletteRequest
        async def receive():
            return {"type": "http.request", "body": body}
        request = StarletteRequest(request.scope, receive)
    
    response = await call_next(request)
    
    logger.info(f"Response status: {response.status_code}")
    
    # Log response body for error responses
    if response.status_code >= 400 and request.url.path in ["/token", "/authorize"]:
        # Note: This won't work for streaming responses, only for JSON/text
        logger.error(f"Error response for {request.url.path}: status {response.status_code}")
    
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
app.mount("/assets/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets_compat")

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
        # Only add CSP header for asset requests, not OAuth pages
        # OAuth pages need to allow form-action to the server and Cloudflare scripts
        if request.url.path.startswith("/assets"):
            response.headers["Content-Security-Policy"] = _get_widget_csp_string()
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
        """Display login page to authenticate user."""
        try:
            # Parse query parameters
            query_params = dict(request.query_params)
            
            client_id = query_params.get("client_id")
            redirect_uri = query_params.get("redirect_uri")
            state = query_params.get("state", "")
            code_challenge = query_params.get("code_challenge")
            scope = query_params.get("scope", " ".join(OAUTH_DEFAULT_SCOPES))
            temp_key = query_params.get("temp_key")
            
            if not client_id or not temp_key:
                return HTMLResponse("<h1>Error: Missing required parameters</h1>", status_code=400)
            
            logger.info(f"Displaying login page for client: {client_id}")
            
            return templates.TemplateResponse(
                "login.html",
                {
                    "request": request,
                    "client_id": client_id,
                    "redirect_uri": redirect_uri,
                    "state": state,
                    "code_challenge": code_challenge,
                    "temp_key": temp_key,
                    "scope": scope,
                }
            )
        except Exception as e:
            logger.error(f"Error in login page: {e}", exc_info=True)
            return HTMLResponse(f"<h1>Error: {str(e)}</h1>", status_code=500)

    async def oauth_login(request: Request):
        """Handle login form submission and show consent page."""
        try:
            # Get form data
            form = await request.form()
            user_id = form.get("user_id")
            client_id = form.get("client_id")
            redirect_uri = form.get("redirect_uri")
            state = form.get("state", "")
            code_challenge = form.get("code_challenge")
            scope = form.get("scope", " ".join(OAUTH_DEFAULT_SCOPES))
            temp_key = form.get("temp_key")
            scopes = scope.split() if scope else OAUTH_DEFAULT_SCOPES
            
            if not user_id or not client_id or not temp_key:
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
            
            logger.info(f"User {user_id} logged in, displaying consent page for client: {client_id}")
            
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
                    "user_email": user_id,  # Use user_id as email/identifier
                }
            )
        except Exception as e:
            logger.error(f"Error in login processing: {e}", exc_info=True)
            return HTMLResponse(f"<h1>Error: {str(e)}</h1>", status_code=500)
    
    async def oauth_authorize_approve(request: Request):
        """Handle authorization approval/denial."""
        try:
            # Get form data
            form = await request.form()
            temp_key = form.get("temp_key")
            approved = form.get("approved", "true") == "true"
            
            if not temp_key:
                return HTMLResponse("<h1>Error: Missing temp_key</h1>", status_code=400)
            
            logger.info(f"Processing authorization approval: approved={approved}, temp_key={temp_key[:8]}...")
            
            # Complete authorization (state is now handled internally)
            redirect_url = await oauth_provider.complete_authorization(temp_key, approved)
            
            if not redirect_url:
                # This is likely a duplicate submission - the auth was already processed
                # Return a friendly message instead of an error
                logger.warning(f"Authorization request already processed or expired: {temp_key[:8]}...")
                return HTMLResponse(
                    "<html><body style='font-family: system-ui; text-align: center; padding: 50px;'>"
                    "<h2>Authorization Already Processed</h2>"
                    "<p>This authorization request has already been completed.</p>"
                    "<p>You can close this window and return to the application.</p>"
                    "</body></html>",
                    status_code=200  # Not an error, just already done
                )
            
            logger.info(f"Redirecting to: {redirect_url}")
            
            return RedirectResponse(url=redirect_url, status_code=302)
            
        except Exception as e:
            logger.error(f"Error in authorization approval: {e}", exc_info=True)
            return HTMLResponse(f"<h1>Error: {str(e)}</h1>", status_code=500)
    
    async def oauth_stats(request: Request):
        """OAuth statistics endpoint (for debugging)."""
        if oauth_provider:
            stats = oauth_provider.get_stats()
            provider_info = oauth_provider.get_provider_info()
            return JSONResponse({
                "oauth_enabled": True,
                "issuer_url": OAUTH_ISSUER_URL,
                "valid_scopes": OAUTH_VALID_SCOPES,
                "default_scopes": OAUTH_DEFAULT_SCOPES,
                **provider_info,
                **stats,
            })
        return JSONResponse({"oauth_enabled": False})
    
    async def google_oauth_callback(request: Request):
        """Handle Google OAuth callback."""
        logger.info(f"Google OAuth callback endpoint hit: {request.url}")
        from oauth_providers.google import GoogleOAuthProvider
        
        if not isinstance(oauth_provider, GoogleOAuthProvider):
            logger.error("OAuth provider is not GoogleOAuthProvider")
            return HTMLResponse("<h1>Error: Google OAuth not configured</h1>", status_code=400)
        
        try:
            code = request.query_params.get("code")
            state = request.query_params.get("state")  # This is our temp_key
            error = request.query_params.get("error")
            
            logger.info(f"Callback params: code={'present' if code else 'missing'}, state={'present' if state else 'missing'}, error={error}")
            
            if error:
                logger.error(f"Google OAuth error: {error}")
                return HTMLResponse(f"<h1>Google Authentication Error</h1><p>{error}</p>", status_code=400)
            
            if not code or not state:
                return HTMLResponse("<h1>Error: Missing code or state</h1>", status_code=400)
            
            # Handle callback and get user info
            callback_data = await oauth_provider.handle_google_callback(code, state)
            
            # Redirect to consent page with user info
            temp_key = callback_data["temp_key"]
            user_info = callback_data["user_info"]
            
            # Store user info temporarily (will be associated with auth code)
            from urllib.parse import urlencode
            consent_params = {
                "temp_key": temp_key,
                "provider": "google",
                "user_email": user_info.get("email", ""),
                "user_name": user_info.get("name", ""),
            }
            
            consent_url = f"{OAUTH_ISSUER_URL}/oauth/consent/page?{urlencode(consent_params)}"
            return RedirectResponse(url=consent_url, status_code=302)
            
        except Exception as e:
            logger.error(f"Error in Google callback: {e}", exc_info=True)
            return HTMLResponse(f"<h1>Error: {str(e)}</h1>", status_code=500)
    
    async def azure_oauth_callback(request: Request):
        """Handle Azure OAuth callback."""
        from oauth_providers.azure import AzureEntraIDProvider
        
        if not isinstance(oauth_provider, AzureEntraIDProvider):
            return HTMLResponse("<h1>Error: Azure OAuth not configured</h1>", status_code=400)
        
        try:
            code = request.query_params.get("code")
            state = request.query_params.get("state")  # This is our temp_key
            error = request.query_params.get("error")
            error_description = request.query_params.get("error_description")
            
            if error:
                logger.error(f"Azure OAuth error: {error} - {error_description}")
                return HTMLResponse(f"<h1>Azure Authentication Error</h1><p>{error}: {error_description}</p>", status_code=400)
            
            if not code or not state:
                return HTMLResponse("<h1>Error: Missing code or state</h1>", status_code=400)
            
            # Handle callback and get user info
            callback_data = await oauth_provider.handle_azure_callback(code, state)
            
            # Redirect to consent page with user info
            temp_key = callback_data["temp_key"]
            user_info = callback_data["user_info"]
            
            from urllib.parse import urlencode
            consent_params = {
                "temp_key": temp_key,
                "provider": "azure",
                "user_email": user_info.get("userPrincipalName", user_info.get("mail", "")),
                "user_name": user_info.get("displayName", ""),
            }
            
            consent_url = f"{OAUTH_ISSUER_URL}/oauth/consent/page?{urlencode(consent_params)}"
            return RedirectResponse(url=consent_url, status_code=302)
            
        except Exception as e:
            logger.error(f"Error in Azure callback: {e}", exc_info=True)
            return HTMLResponse(f"<h1>Error: {str(e)}</h1>", status_code=500)
    
    async def oauth_consent_page(request: Request):
        """Display consent page after external OAuth (Google/Azure)."""
        try:
            temp_key = request.query_params.get("temp_key")
            provider = request.query_params.get("provider", "custom")
            user_email = request.query_params.get("user_email", "")
            user_name = request.query_params.get("user_name", "")
            
            if not temp_key:
                return HTMLResponse("<h1>Error: Missing temp_key</h1>", status_code=400)
            
            # Get provider info for branding
            provider_info = oauth_provider.get_provider_info()
            
            scope_descriptions = {
                "read": "View AT&T products, services, and store locations",
                "write": "Make changes to your account and preferences",
                "payment": "Process payments on your behalf",
                "account": "Access your account information",
            }
            
            return templates.TemplateResponse(
                "authorize.html",
                {
                    "request": request,
                    "client_id": "chatgpt",
                    "client_name": "ChatGPT",
                    "redirect_uri": "",
                    "state": "",
                    "code_challenge": "",
                    "temp_key": temp_key,
                    "scopes": OAUTH_DEFAULT_SCOPES,
                    "scopes_str": " ".join(OAUTH_DEFAULT_SCOPES),
                    "scope_descriptions": scope_descriptions,
                    "action_url": "/oauth/consent/approve",
                    "provider": provider,
                    "provider_name": provider_info.get("name", provider),
                    "user_email": user_email,
                    "user_name": user_name,
                }
            )
        except Exception as e:
            logger.error(f"Error in consent page: {e}", exc_info=True)
            return HTMLResponse(f"<h1>Error: {str(e)}</h1>", status_code=500)
    
    async def oauth_consent_approve(request: Request):
        """Handle consent approval for external OAuth providers."""
        try:
            form = await request.form()
            temp_key = form.get("temp_key")
            approved = form.get("approved", "true") == "true"
            user_info_str = form.get("user_info", "{}")
            
            if not temp_key:
                return HTMLResponse("<h1>Error: Missing temp_key</h1>", status_code=400)
            
            logger.info(f"Processing consent approval: approved={approved}, temp_key={temp_key[:8]}...")
            
            # Parse user info if provided
            import json
            user_info = json.loads(user_info_str) if user_info_str != "{}" else None
            
            # Complete authorization with user info
            redirect_url = await oauth_provider.complete_authorization(temp_key, approved, user_info)
            
            if not redirect_url:
                return HTMLResponse("<h1>Error: Authorization request expired or invalid</h1>", status_code=400)
            
            logger.info(f"Redirecting to: {redirect_url}")
            return RedirectResponse(url=redirect_url, status_code=302)
            
        except Exception as e:
            logger.error(f"Error in consent approval: {e}", exc_info=True)
            return HTMLResponse(f"<h1>Error: {str(e)}</h1>", status_code=500)
    
    # Add OAuth routes
    app.add_route("/oauth/authorize/page", oauth_authorize_page, methods=["GET"])
    app.add_route("/oauth/login", oauth_login, methods=["POST"])
    app.add_route("/oauth/authorize/approve", oauth_authorize_approve, methods=["POST"])
    app.add_route("/oauth/google/callback", google_oauth_callback, methods=["GET"])
    app.add_route("/oauth/azure/callback", azure_oauth_callback, methods=["GET"])
    app.add_route("/oauth/consent/page", oauth_consent_page, methods=["GET"])
    app.add_route("/oauth/consent/approve", oauth_consent_approve, methods=["POST"])
    app.add_route("/oauth/stats", oauth_stats, methods=["GET"])
    
    logger.info("OAuth endpoints registered: /oauth/authorize/page, /oauth/authorize/approve, /oauth/google/callback, /oauth/azure/callback, /oauth/consent/page, /oauth/stats")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000)
