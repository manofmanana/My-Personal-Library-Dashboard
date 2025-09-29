import sqlite3
import pandas as pd
import requests
import re
from difflib import SequenceMatcher
from urllib.parse import quote_plus
from typing import Optional, Dict, Any

DB_PATH = "books_normalized.db"

# =====================
# Database Helpers
# =====================

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def get_books() -> pd.DataFrame:
    """Return books with author, genre, and average rating."""
    conn = get_connection()
    query = """
    SELECT
        b.id,
        b.title,
        a.name AS author,
        g.name AS genre,
        b.year,
        b.isbn,
        b.subjects,
        b.cover_url,
        ROUND(AVG(r.rating), 2) AS rating
    FROM books b
    LEFT JOIN authors a ON b.author_id = a.id
    LEFT JOIN genres g ON b.genre_id = g.id
    LEFT JOIN ratings r ON b.id = r.book_id
    GROUP BY b.id
    ORDER BY b.year DESC, b.title;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def _get_or_create_author(conn: sqlite3.Connection, name: str) -> int:
    c = conn.cursor()
    c.execute("SELECT id FROM authors WHERE name=?", (name,))
    row = c.fetchone()
    if row:
        return row[0]
    c.execute("INSERT INTO authors (name) VALUES (?)", (name,))
    conn.commit()
    return c.lastrowid

def _get_or_create_genre(conn: sqlite3.Connection, name: str) -> int:
    c = conn.cursor()
    c.execute("SELECT id FROM genres WHERE name=?", (name,))
    row = c.fetchone()
    if row:
        return row[0]
    c.execute("INSERT INTO genres (name) VALUES (?)", (name,))
    conn.commit()
    return c.lastrowid

def add_book(title: str, author: str, genre: str, year: int,
             rating: float, isbn: Optional[str] = None,
             subjects: Optional[str] = None, cover_url: Optional[str] = None):
    """Insert new book + rating. If cover/subjects missing, try to fetch."""
    conn = get_connection()
    c = conn.cursor()

    author_id = _get_or_create_author(conn, author or "Unknown")

    if not subjects and not cover_url:
        fetched = fetch_book_data(title, author, isbn if isbn else None)
        cover_url = cover_url or fetched.get("cover_url")
        subjects = subjects or fetched.get("subjects")
        if fetched.get("isbn"):
            isbn = fetched["isbn"]

    genre_name = genre or (subjects.split(",")[0] if subjects else "Unknown")
    genre_id = _get_or_create_genre(conn, genre_name)

    c.execute("""
        INSERT INTO books (title, author_id, genre_id, year, isbn, subjects, cover_url)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (title, author_id, genre_id, year, isbn, subjects, cover_url))
    book_id = c.lastrowid

    if rating is not None:
        c.execute("INSERT INTO ratings (book_id, rating) VALUES (?, ?)", (book_id, float(rating)))

    conn.commit()
    conn.close()

def update_book(book_id: int, title: str, author: str, genre: str, year: int,
                rating: float, isbn: Optional[str] = None,
                subjects: Optional[str] = None, cover_url: Optional[str] = None):
    """
    Update an existing book with edited values from the form.
    Overwrites all editable fields and replaces rating.
    """
    conn = get_connection()
    try:
        c = conn.cursor()

        # Resolve author and genre IDs (create if missing)
        author_id = _get_or_create_author(conn, author or "Unknown")
        genre_name = genre or (subjects.split(",")[0] if subjects else "Unknown")
        genre_id = _get_or_create_genre(conn, genre_name)

        # Update book core fields
        c.execute("""
            UPDATE books
            SET title=?, author_id=?, genre_id=?, year=?, isbn=?, subjects=?, cover_url=?
            WHERE id=?
        """, (title, author_id, genre_id, year, isbn, subjects, cover_url, book_id))

        # Replace rating(s) with new one
        c.execute("DELETE FROM ratings WHERE book_id=?", (book_id,))
        if rating is not None:
            c.execute("INSERT INTO ratings (book_id, rating) VALUES (?, ?)", (book_id, float(rating)))

        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def delete_book(book_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM ratings WHERE book_id=?", (book_id,))
    c.execute("DELETE FROM books WHERE id=?", (book_id,))
    conn.commit()
    conn.close()

# =====================
# Open Library link
# =====================

def openlibrary_link(title: str, author: str, isbn: Optional[str]) -> str:
    if isbn and str(isbn).strip():
        return f"https://openlibrary.org/isbn/{str(isbn).strip()}"
    q = " ".join([x for x in [(title or '').strip(), (author or '').strip()] if x])
    return f"https://openlibrary.org/search?q={quote_plus(q)}"

# =====================
# Cover Fetching
# =====================

def _normalize_text(s: str) -> str:
    s = s or ""
    s = s.strip().lower()
    s = re.sub(r"[’'`]", "'", s)
    s = re.sub(r"[^a-z0-9\s:,-]", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s

def _title_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, _normalize_text(a), _normalize_text(b)).ratio()

def fetch_cover_by_isbn(isbn: str) -> Optional[str]:
    if not isbn:
        return None
    try:
        r = requests.get(f"https://openlibrary.org/isbn/{isbn}.json", timeout=10)
        if r.status_code == 200:
            js = r.json()
            if isinstance(js, dict) and "covers" in js and js["covers"]:
                cover_id = js["covers"][0]
                return f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
    except Exception:
        pass
    return f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg"

def fetch_openlibrary_best(title: str, author: Optional[str]) -> Dict[str, Optional[str]]:
    attempts = []
    if author:
        attempts.append({"title": title, "author": author})
    attempts.append({"title": title})
    attempts.append({"q": f"{title} {author or ''}".strip()})

    for params in attempts:
        try:
            r = requests.get("https://openlibrary.org/search.json", params=params, timeout=10)
            if r.status_code != 200:
                continue
            docs = (r.json() or {}).get("docs", []) or []
            if not docs:
                continue
            best = docs[0]
            cover_url = f"https://covers.openlibrary.org/b/id/{best['cover_i']}-L.jpg" if "cover_i" in best else None
            isbn = (best.get("isbn") or [None])[0]
            subjects = ", ".join((best.get("subject") or [])[:5]) if best.get("subject") else None
            return {"cover_url": cover_url, "isbn": isbn, "subjects": subjects}
        except Exception:
            continue
    return {"cover_url": None, "isbn": None, "subjects": None}

def fetch_cover_google_books(title: str, author: Optional[str]) -> Optional[str]:
    q = f'intitle:"{title}"'
    if author:
        q += f'+inauthor:"{author}"'
    try:
        r = requests.get("https://www.googleapis.com/books/v1/volumes",
                         params={"q": q, "maxResults": 5}, timeout=10)
        items = (r.json() or {}).get("items", [])
        for it in items:
            links = (it.get("volumeInfo") or {}).get("imageLinks") or {}
            for key in ["extraLarge", "large", "medium", "small", "thumbnail"]:
                if links.get(key):
                    return links[key]
    except Exception:
        pass
    return None

def fetch_book_data(title: str, author: Optional[str], isbn: Optional[str]) -> Dict[str, Optional[str]]:
    if isbn and str(isbn).strip():
        cover_isbn = fetch_cover_by_isbn(str(isbn).strip())
        if cover_isbn:
            return {"cover_url": cover_isbn, "isbn": isbn, "subjects": None}
    ol = fetch_openlibrary_best(title, author)
    if ol.get("cover_url"):
        return ol
    gb = fetch_cover_google_books(title, author)
    if gb:
        return {"cover_url": gb, "isbn": isbn, "subjects": None}
    return {"cover_url": "https://via.placeholder.com/256x384.png?text=No+Cover",
            "isbn": isbn, "subjects": None}

def get_or_fetch_cover_for_row(row: pd.Series) -> str:
    current = (row.get("cover_url") or "").strip()
    if current:
        return current
    fetched = fetch_book_data(row.get("title") or "", row.get("author"), row.get("isbn"))
    cover_url = (fetched.get("cover_url") or "").strip()
    if cover_url:
        conn = get_connection()
        c = conn.cursor()
        c.execute("UPDATE books SET cover_url=?, isbn=?, subjects=? WHERE id=?",
                  (cover_url, fetched.get("isbn") or row.get("isbn"),
                   fetched.get("subjects") or row.get("subjects"), int(row["id"])))
        conn.commit()
        conn.close()
        return cover_url
    return "https://via.placeholder.com/256x384.png?text=No+Cover"

def rebuild_covers() -> int:
    """Refetch covers/subjects for every book using title/author/isbn."""
    conn = get_connection()
    df = pd.read_sql("""
        SELECT b.id, b.title, b.isbn, a.name AS author
        FROM books b LEFT JOIN authors a ON b.author_id = a.id
    """, conn)
    updated = 0
    c = conn.cursor()
    for _, r in df.iterrows():
        fetched = fetch_book_data(r["title"], r["author"], r["isbn"])
        cover_url = (fetched.get("cover_url") or "").strip()
        if cover_url:
            c.execute("UPDATE books SET cover_url=?, isbn=?, subjects=? WHERE id=?",
                      (cover_url, fetched.get("isbn") or r["isbn"], fetched.get("subjects"), int(r["id"])))
            updated += 1
    conn.commit()
    conn.close()
    return updated
