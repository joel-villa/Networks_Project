import mwparserfromhell
from mwparserfromhell.nodes import Text, Wikilink, ExternalLink, Heading, Tag, HTMLEntity, Template
# Below are imports for testing
try:
    from .getWikitext import getWikitext
except ImportError:
    from getWikitext import getWikitext


def translate(wikitext: str) -> str:
    """
    AI written. Translates core wikitext nodes to HTML, ignoring templates and media assets.
    """
    # Parse the raw wikitext into an Abstract Syntax Tree (AST)
    wikicode = mwparserfromhell.parse(wikitext)
    
    def process_nodes(nodes) -> str:
        html_parts = []
        
        for node in nodes:
            # 1. Standard Text
            if isinstance(node, Text):
                html_parts.append(str(node.value))
                
            # 2. Section Headings
            elif isinstance(node, Heading):
                level = node.level
                # Recursively parse the title in case it contains links or formatting
                title_html = process_nodes(node.title.nodes)
                html_parts.append(f"<h{level}>{title_html.strip()}</h{level}>\n")
                
            # 3. Internal MediaWiki Links
            elif isinstance(node, Wikilink):
                title_str = str(node.title).strip()
                lower_title = title_str.lower()
                
                # Ignore non-text assets and metadata categories
                if lower_title.startswith(("file:", "image:", "media:", "category:")):
                    continue
                
                # If there's a custom label (e.g. [[Page|Label]]), recursively parse it. 
                # Otherwise, use the page title as the label.
                if node.text:
                    label_html = process_nodes(node.text.nodes)
                else:
                    label_html = title_str
                    
                html_parts.append(f'<a href="/wiki/{title_str}">{label_html}</a>')
                
            # 4. External Web Links
            elif isinstance(node, ExternalLink):
                url_str = str(node.url).strip()
                # External links use node.title for their readable text label
                if node.title:
                    label_html = process_nodes(node.title.nodes)
                else:
                    label_html = url_str
                
                html_parts.append(f'<a href="{url_str}">{label_html}</a>')
                
            # 5. HTML Tags and Wiki Visual Formatting (Bold, Italics, etc.)
            elif isinstance(node, Tag):
                # mwparserfromhell normalizes wiki markup (''') into HTML tags (b, i, etc.)
                tag_name = str(node.tag).strip().lower()
                
                if node.self_closing:
                    html_parts.append(f"<{tag_name} />")
                else:
                    inner_html = process_nodes(node.contents.nodes) if node.contents else ""
                    html_parts.append(f"<{tag_name}>{inner_html}</{tag_name}>")
                    
            # 6. HTML Entities
            elif isinstance(node, HTMLEntity):
                html_parts.append(str(node.value))
                
            # 7. Templates (Ignored completely)
            elif isinstance(node, Template):
                pass 
            
            # (Comments and Arguments are also naturally ignored by not matching the above)
            
        return "".join(html_parts)

    # Start the recursive processing at the root level of the AST
    return process_nodes(wikicode.nodes)


def generatePage(title: str, wikitext: str):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
</head>
<body>
    <h1>{title}</h1>
    {translate(wikitext)}
</body>
</html>"""


def main():
    pageName = "Iran"
    page = getWikitext(pageName)
    print(generatePage(pageName, page))

if __name__ == "__main__":
    main()
