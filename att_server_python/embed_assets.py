"""Script to embed JS and CSS directly into HTML files to avoid ngrok browser warnings."""

from pathlib import Path
import re

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"

def embed_assets_in_html(html_path: Path) -> str:
    """Read an HTML file and embed all external JS and CSS files directly into it."""
    html = html_path.read_text(encoding="utf8")

    # Find all script tags with src
    script_pattern = r'<script[^>]*src="([^"]+)"[^>]*></script>'
    for match in re.finditer(script_pattern, html):
        src_url = match.group(1)
        # Extract filename from URL
        filename = src_url.split('/')[-1]
        js_path = ASSETS_DIR / filename

        if js_path.exists():
            js_content = js_path.read_text(encoding="utf8")
            # Replace external script with inline script
            inline_script = f'<script type="module">\n{js_content}\n</script>'
            html = html.replace(match.group(0), inline_script)
            print(f"Embedded: {filename}")

    # Find all link tags with href (CSS)
    link_pattern = r'<link[^>]*href="([^"]+)"[^>]*>'
    for match in re.finditer(link_pattern, html):
        href_url = match.group(1)
        # Extract filename from URL
        filename = href_url.split('/')[-1]
        css_path = ASSETS_DIR / filename

        if css_path.exists():
            css_content = css_path.read_text(encoding="utf8")
            # Replace external link with inline style
            inline_style = f'<style>\n{css_content}\n</style>'
            html = html.replace(match.group(0), inline_style)
            print(f"Embedded: {filename}")

    return html


if __name__ == "__main__":
    # Test with att-store-finder
    html_path = ASSETS_DIR / "att-store-finder.html"
    if html_path.exists():
        embedded_html = embed_assets_in_html(html_path)
        print(f"\nGenerated HTML length: {len(embedded_html)} bytes")
        print(f"Original HTML length: {len(html_path.read_text())} bytes")
    else:
        print(f"HTML file not found: {html_path}")
