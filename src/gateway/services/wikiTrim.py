import mwparserfromhell
from mwparserfromhell.nodes import Text, Wikilink, ExternalLink, Heading, Tag, HTMLEntity, Template
# Below are imports for testing
import sys
from pathlib import Path

# Add project root to sys.path so direct script execution can resolve other packages
_project_root = str(Path(__file__).resolve().parents[3])
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

try:
    from ...client.services.getWikitext import getWikitext
except (ImportError, ValueError):
    from src.client.services.getWikitext import getWikitext


def shouldRemove(node) -> bool:
    """
    Return false for
    1. Templates
    2. File, image, media, and category Wikilinks
    3. Comments, arguments, non-whitelisted node types
    """
    if isinstance(node, Template):
        return True

    if isinstance(node, Wikilink):
        lower_title = str(node.title).strip().lower()
        if lower_title.startswith(("file:", "image:", "media:", "category:")):
            return True

    if not isinstance(node, (Text, Heading, Wikilink, ExternalLink, Tag, HTMLEntity)):
        return True

    return False


def cleanWikicode(wc) -> None:
    if not hasattr(wc, "nodes"):
        return

    # Use a list snapshot to safely remove nodes during iteration
    for node in list(wc.nodes):
        if shouldRemove(node):
            try:
                wc.remove(node, recursive=False)
            except ValueError:
                pass
        else:
            cleanNode(node)


def cleanNode(node) -> None:
    if isinstance(node, Heading):
        cleanWikicode(node.title)
    elif isinstance(node, Tag):
        if node.contents:
            cleanWikicode(node.contents)
    elif isinstance(node, Wikilink):
        if node.title:
            cleanWikicode(node.title)
        if node.text:
            cleanWikicode(node.text)
    elif isinstance(node, ExternalLink):
        if node.title:
            cleanWikicode(node.title)


def trim(raw: str) -> str:
    """
    Parses raw wikitext and strips out all AST nodes that are ignored
    by wikitohtml.py (such as Templates, media/category Wikilinks, Comments,
    and Arguments). Returns the cleaned wikitext string.
    """
    if not raw:
        return ""

    wikicode = mwparserfromhell.parse(raw)
    cleanWikicode(wikicode)
    return str(wikicode)

#main only used for testing
def main():
    wikitext = getWikitext("Iran")
    print(f"Size before trimming: {len(wikitext)} characters")
    result = trim(wikitext)
    print(f"Size after trimming: {len(result)} characters")

if __name__ == "__main__":
    main()