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
from pydantic import BaseModel, ConfigDict, Field, ValidationError


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


@lru_cache(maxsize=None)
def _load_widget_html(component_name: str) -> str:
    html_path = ASSETS_DIR / f"{component_name}.html"
    if html_path.exists():
        return html_path.read_text(encoding="utf8")

    fallback_candidates = sorted(ASSETS_DIR.glob(f"{component_name}-*.html"))
    if fallback_candidates:
        return fallback_candidates[-1].read_text(encoding="utf8")

    raise FileNotFoundError(
        f'Widget HTML for "{component_name}" not found in {ASSETS_DIR}. '
        "Run `pnpm run build` to generate the assets before starting the server."
    )


widgets: List[ATTWidget] = [
    ATTWidget(
        identifier="att-store-locator",
        title="Find AT&T Stores & Services",
        template_uri="ui://widget/att-store-locator.html",
        invoking="Locating AT&T stores and services",
        invoked="Found AT&T locations",
        html=_load_widget_html("att-store-finder"),
        response_text="Displayed AT&T store locations with available products and services!",
    ),
    ATTWidget(
        identifier="att-products-carousel",
        title="Browse AT&T Products",
        template_uri="ui://widget/att-products-carousel.html",
        invoking="Loading AT&T products",
        invoked="Products loaded",
        html=_load_widget_html("att-products-carousel"),
        response_text="Displayed AT&T products carousel with cell phones, plans, and accessories!",
    ),
    ATTWidget(
        identifier="att-services-gallery",
        title="View AT&T Services",
        template_uri="ui://widget/att-services-gallery.html",
        invoking="Loading AT&T services",
        invoked="Services loaded",
        html=_load_widget_html("att-products-albums"),
        response_text="Displayed AT&T services including Wireless, Fiber, and Internet Air!",
    ),
    ATTWidget(
        identifier="att-plans-list",
        title="Compare AT&T Plans",
        template_uri="ui://widget/att-plans-list.html",
        invoking="Loading plan options",
        invoked="Plans loaded",
        html=_load_widget_html("att-products-list"),
        response_text="Displayed AT&T wireless plans with pricing and features!",
    ),
    ATTWidget(
        identifier="att-for-you",
        title="For You - Personalized Recommendations",
        template_uri="ui://widget/att-for-you.html",
        invoking="Loading personalized recommendations",
        invoked="Recommendations loaded",
        html=_load_widget_html("att-for-you"),
        response_text="Displayed personalized AT&T offers and recommendations tailored to your account!",
    ),
    ATTWidget(
        identifier="att-internet-backup-offer",
        title="Internet Backup Offer",
        template_uri="ui://widget/att-internet-backup-offer.html",
        invoking="Loading Internet Backup offer",
        invoked="Offer loaded",
        html=_load_widget_html("att-internet-backup-offer"),
        response_text="Displayed Internet Backup offer - stay connected even during outages!",
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
        description="Type of AT&T product or service (e.g., 'cell phones', 'wireless plans', 'fiber internet', '5g coverage').",
    )

    model_config = ConfigDict(populate_by_name=True, extra="forbid")


mcp = FastMCP(
    name="att-products-python",
    stateless_http=True,
)


TOOL_INPUT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "productType": {
            "type": "string",
            "description": "Type of AT&T product or service (e.g., 'cell phones', 'wireless plans', 'fiber internet', '5g coverage').",
        }
    },
    "required": ["productType"],
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
    return [
        types.Tool(
            name=widget.identifier,
            title=widget.title,
            description=widget.title,
            inputSchema=deepcopy(TOOL_INPUT_SCHEMA),
            _meta=_tool_meta(widget),
            # To disable the approval prompt for the tools
            annotations={
                "destructiveHint": False,
                "openWorldHint": False,
                "readOnlyHint": True,
            },
        )
        for widget in widgets
    ]


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
            structuredContent={"productType": product_type},
            _meta=meta
        )
    )


mcp._mcp_server.request_handlers[types.CallToolRequest] = _call_tool_request
mcp._mcp_server.request_handlers[types.ReadResourceRequest] = _handle_read_resource


app = mcp.streamable_http_app()

try:
    from starlette.middleware.cors import CORSMiddleware

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=False,
    )
except Exception:
    pass


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000)
