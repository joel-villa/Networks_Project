r = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "raw",
                "format": "json",
                "generator": "search",
                "gsrsearch": "Cats",
                "gsrlimit": 1,
                "prop": "extracts",
                "exintro": 1,
                "explaintext": 1,
                "redirects": 1,
            },
            headers={"User-Agent": "Meshcodre"},
            timeout=8,
        )
        r.raise_for_status()
        pages = r.json().get("query", {}).get("pages", {})
        # https://en.wikipedia.org/w/index.php?title=Pet_door&action=raw   