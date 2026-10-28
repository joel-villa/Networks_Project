import requests

def getWikitext(page_title: str) -> str | None:
    url = f"https://en.wikipedia.org/w/api.php"
    
    params = {
        "action": "query",
        "prop": "revisions",
        "rvprop": "content",
        "rvslots": "main",
        "titles": page_title,
        "format": "json"
    }

    headers={"User-Agent": "pleaseWiki"}

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()

        pages = data.get("query", {}).get("pages", {})
        
        for page_id, page_info in pages.items():
            if page_id == "-1":
                print(f"Page '{page_title}' does not exist.")
                return None
                
            revisions = page_info.get("revisions", [])
            if revisions:
                return revisions[0]["slots"]["main"]["*"]
                
    except requests.RequestException as e:
        print(f"Network error occurred: {e}")
        return None
    except KeyError as e:
        print(f"Unexpected response structure: {e}")
        return None

if __name__ == "__main__":
    title = "Help:Wikitext"
    wikitext = getWikitext(title)
    print(wikitext)