# from getWikitext import getWikitext
# todo: maybe making the folders python packages
try:
    from .getWikitext import getWikitext
except ImportError:
    from getWikitext import getWikitext
## TODO, check out all wikitext formatting, do them all?


def formatParagraph(paragraphText: str) -> str:
    result = doFaces(paragraphText)
    result = doLinks(result)

    return tagify(result, "p")


def doLinks(text: str) -> str:
    links = text.split("[[")
    result = ""
    for i in range(len(links)):
        if not "]]" in links[i]:
            result += links[i]
        else:
            parts = links[i].split("]]")
            result += formatLink(parts[0])
            result += parts[1]
    return result


def doFaces(text: str) -> str:
    result = ""
    phrases = text.split("'''''")
    for i in range(len(phrases)):
        if i % 2 == 1:
            result += tagify(tagify(phrases[i], "em"), "b")
        else:
            result += phrases[i]
    phrases = result.split("'''")
    result = ""
    for i in range(len(phrases)):
        if i % 2 == 1:
            result += tagify(phrases[i], "b")
        else:
            result += phrases[i]
    phrases = result.split("''")
    result = ""
    for i in range(len(phrases)):
        if i % 2 == 1:
            result += tagify(phrases[i], "em")
        else:
            result += phrases[i]
    return result


def formatLink(wikitextLink: str) -> str:
    parts = wikitextLink.split("|")
    if len(parts) == 1:
        return tagifyArgs(wikitextLink, "a", "href", parts[0])
    elif len(parts) == 2:
        return tagifyArgs(parts[1], "a", "href", parts[0])
    elif len(parts) == 3:
        return f"Image '{parts[0]}' of '{parts[2]}'"
    return ""


def tagify(content: str, type: str) -> str:
    return f"<{type}>{content}</{type}>"


def tagifyArgs(content: str, type: str, argName: str, argVal: str) -> str:
    return f"<{type} {argName}='{argVal}'>{content}</{type}>"


def processChunk(wikitextChunk: str) -> str:
    result = ""
    paragraphs = wikitextChunk.split("\n")
    for p in paragraphs:
        para = p.strip()
        if para[0] == para[len(para) - 1] == "=":
            result += makeHeader(para)
        else:
            result += formatParagraph(para)
    return result


def makeHeader(headerStr: str) -> str:
    hLevel = headerStr.count("=") / 2
    return tagify(headerStr.replace("=", ""), f"h{int(hLevel)}")


def translate(wikitext: str) -> str:
    result = ""
    chunks = wikitext.split("\n\n")
    for chunk in chunks:
        result += processChunk(chunk)
    return result


def generatePage(title: str, wikitext: str):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Minimal HTML Document</title>
</head>
<body>
{tagify(title, "h1")}
{translate(wikitext)}
</body>
</html>"""


def main():
    pageName = "Help:Wikitext"
    page = getWikitext(pageName)
    print(generatePage(pageName, page))


if __name__ == "__main__":
    main()
