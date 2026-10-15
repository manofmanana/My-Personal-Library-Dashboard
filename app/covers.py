"""Looking up a book's cover, ISBN, and subjects online (Open Library first, then Google Books)."""
from typing import Dict, Optional

import requests

TIMEOUT = 6  # seconds per request
NOT_FOUND = {"cover_url": None, "isbn": None, "subjects": None}


def _get_json(url: str, **params) -> Optional[dict]:
    try:
        response = requests.get(url, params=params or None, timeout=TIMEOUT)
        if response.ok:
            return response.json()
    except (requests.RequestException, ValueError):
        pass
    return None


def cover_from_isbn(isbn: str) -> Optional[str]:
    data = _get_json(f"https://openlibrary.org/isbn/{isbn}.json")
    if data and data.get("covers"):
        return f"https://covers.openlibrary.org/b/id/{data['covers'][0]}-L.jpg"
    return None


def search_open_library(title: str, author: Optional[str]) -> Dict[str, Optional[str]]:
    """Try title+author, then title alone, then a free-text search; use the first match with a cover."""
    attempts = [{"title": title, "author": author}] if author else []
    attempts += [{"title": title}, {"q": f"{title} {author or ''}".strip()}]
    for params in attempts:
        data = _get_json("https://openlibrary.org/search.json", **params, limit=5) or {}
        for doc in data.get("docs") or []:
            if doc.get("cover_i"):
                return {
                    "cover_url": f"https://covers.openlibrary.org/b/id/{doc['cover_i']}-L.jpg",
                    "isbn": (doc.get("isbn") or [None])[0],
                    "subjects": ", ".join((doc.get("subject") or [])[:5]) or None,
                }
    return dict(NOT_FOUND)


def search_google_books(title: str, author: Optional[str]) -> Optional[str]:
    query = f'intitle:"{title}"' + (f'+inauthor:"{author}"' if author else "")
    data = _get_json("https://www.googleapis.com/books/v1/volumes", q=query, maxResults=5) or {}
    for item in data.get("items") or []:
        links = (item.get("volumeInfo") or {}).get("imageLinks") or {}
        for size in ("extraLarge", "large", "medium", "small", "thumbnail"):
            if links.get(size):
                return links[size].replace("http://", "https://")
    return None


def look_up_book(title: str, author: Optional[str] = None, isbn: Optional[str] = None) -> Dict[str, Optional[str]]:
    """Best-effort cover/ISBN/subjects for a book. Any field can be None if nothing was found."""
    isbn = (isbn or "").strip() or None
    if isbn:
        cover = cover_from_isbn(isbn)
        if cover:
            return {"cover_url": cover, "isbn": isbn, "subjects": None}
    found = search_open_library(title, author)
    if found["cover_url"]:
        return {**found, "isbn": isbn or found["isbn"]}
    cover = search_google_books(title, author)
    return {"cover_url": cover, "isbn": isbn, "subjects": None}
