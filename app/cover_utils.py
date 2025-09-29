import requests, re
from difflib import SequenceMatcher
from typing import Optional, Dict
from urllib.parse import quote_plus

def normalize_text(s: str) -> str:
    s = s or ""
    s = s.strip().lower()
    s = re.sub(r"[’'`]", "'", s)
    s = re.sub(r"[^a-z0-9\s:,-]", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s

def title_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, normalize_text(a), normalize_text(b)).ratio()

def fetch_cover_by_isbn(isbn: str) -> Optional[str]:
    if not isbn:
        return None
    try:
        r = requests.get(f"https://openlibrary.org/isbn/{isbn}.json", timeout=10)
        if r.status_code == 200:
            js = r.json()
            if "covers" in js and js["covers"]:
                return f"https://covers.openlibrary.org/b/id/{js['covers'][0]}-L.jpg"
    except:
        pass
    return f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg"

def fetch_openlibrary_best(title: str, author: Optional[str]) -> Dict[str, Optional[str]]:
    try:
        q = " ".join([x for x in [title, author] if x])
        r = requests.get("https://openlibrary.org/search.json", params={"q": q}, timeout=10)
        docs = (r.json() or {}).get("docs", [])
        if not docs: return {"cover_url": None, "isbn": None}
        best = docs[0]
        cover_url = f"https://covers.openlibrary.org/b/id/{best.get('cover_i')}-L.jpg" if best.get("cover_i") else None
        isbn = (best.get("isbn") or [None])[0]
        return {"cover_url": cover_url, "isbn": isbn}
    except:
        return {"cover_url": None, "isbn": None}

def fetch_google_books(title: str, author: Optional[str]) -> Optional[str]:
    q = f'intitle:"{title}"'
    if author: q += f'+inauthor:"{author}"'
    try:
        r = requests.get("https://www.googleapis.com/books/v1/volumes", params={"q": q, "maxResults": 5}, timeout=10)
        items = (r.json() or {}).get("items", [])
        for it in items:
            links = (it.get("volumeInfo") or {}).get("imageLinks") or {}
            for key in ["extraLarge", "large", "medium", "small", "thumbnail"]:
                if links.get(key): return links[key]
    except:
        pass
    return None

def fetch_book_cover(title: str, author: Optional[str], isbn: Optional[str]) -> str:
    if isbn:
        cover = fetch_cover_by_isbn(isbn)
        if cover: return cover
    ol = fetch_openlibrary_best(title, author)
    if ol.get("cover_url"): return ol["cover_url"]
    gb = fetch_google_books(title, author)
    if gb: return gb
    return "https://via.placeholder.com/256x384.png?text=No+Cover"
