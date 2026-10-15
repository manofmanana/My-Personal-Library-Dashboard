"""Reading and writing the library database (see schema.sql for the tables)."""
import os
import sqlite3
from contextlib import contextmanager
from typing import Optional
from urllib.parse import quote_plus

import pandas as pd

DB_PATH = os.environ.get("LIBRARY_DB", "books_normalized.db")

# Added to older copies of the database on startup; IF NOT EXISTS makes it safe to repeat
INDEXES = """
CREATE INDEX IF NOT EXISTS idx_books_author ON books(author_id);
CREATE INDEX IF NOT EXISTS idx_books_genre ON books(genre_id);
CREATE INDEX IF NOT EXISTS idx_books_year ON books(year);
CREATE INDEX IF NOT EXISTS idx_ratings_book ON ratings(book_id);
"""


@contextmanager
def connect(db_path: Optional[str] = None):
    """A connection that commits on success, rolls back on error, and always closes."""
    conn = sqlite3.connect(db_path or DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        with conn:
            yield conn
    finally:
        conn.close()


def get_books(db_path: Optional[str] = None) -> pd.DataFrame:
    """Every book with its author, genre, and average rating, newest reads first."""
    with connect(db_path) as conn:
        return pd.read_sql(
            """
            SELECT b.id, b.title, a.name AS author, g.name AS genre, b.year, b.isbn, b.subjects,
                   b.cover_url, ROUND(AVG(r.rating), 2) AS rating
            FROM books b
            LEFT JOIN authors a ON b.author_id = a.id
            LEFT JOIN genres g ON b.genre_id = g.id
            LEFT JOIN ratings r ON b.id = r.book_id
            GROUP BY b.id
            ORDER BY b.year DESC, b.id DESC
            """,
            conn,
        )


def _get_or_create(conn: sqlite3.Connection, table: str, name: str) -> int:
    """Find an author/genre by name (ignoring capitalization) or add it. Returns its id."""
    row = conn.execute(f"SELECT id FROM {table} WHERE lower(name) = lower(?)", (name,)).fetchone()
    if row:
        return row[0]
    return conn.execute(f"INSERT INTO {table} (name) VALUES (?)", (name,)).lastrowid


def _genre_name(genre: str, subjects: Optional[str]) -> str:
    return genre or (subjects.split(",")[0].strip() if subjects else "") or "Unknown"


def add_book(title: str, author: str, genre: str, year: int, rating: Optional[float],
             isbn: Optional[str] = None, subjects: Optional[str] = None,
             cover_url: Optional[str] = None, db_path: Optional[str] = None) -> int:
    """Add a book (and its rating). Returns the new book's id."""
    with connect(db_path) as conn:
        author_id = _get_or_create(conn, "authors", author or "Unknown")
        genre_id = _get_or_create(conn, "genres", _genre_name(genre, subjects))
        book_id = conn.execute(
            "INSERT INTO books (title, author_id, genre_id, year, isbn, subjects, cover_url) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (title, author_id, genre_id, int(year), isbn, subjects, cover_url),
        ).lastrowid
        if rating is not None:
            conn.execute("INSERT INTO ratings (book_id, rating) VALUES (?, ?)", (book_id, float(rating)))
        tidy(conn)
    return book_id


def update_book(book_id: int, title: str, author: str, genre: str, year: int, rating: Optional[float],
                isbn: Optional[str] = None, subjects: Optional[str] = None,
                cover_url: Optional[str] = None, db_path: Optional[str] = None) -> None:
    """Overwrite a book's details and replace its rating."""
    book_id = int(book_id)  # numpy ints would be stored as raw bytes by sqlite
    with connect(db_path) as conn:
        author_id = _get_or_create(conn, "authors", author or "Unknown")
        genre_id = _get_or_create(conn, "genres", _genre_name(genre, subjects))
        conn.execute(
            "UPDATE books SET title=?, author_id=?, genre_id=?, year=?, isbn=?, subjects=?, cover_url=? WHERE id=?",
            (title, author_id, genre_id, int(year), isbn, subjects, cover_url, book_id),
        )
        conn.execute("DELETE FROM ratings WHERE book_id = ?", (book_id,))
        if rating is not None:
            conn.execute("INSERT INTO ratings (book_id, rating) VALUES (?, ?)", (book_id, float(rating)))
        tidy(conn)


def delete_book(book_id: int, db_path: Optional[str] = None) -> None:
    book_id = int(book_id)
    with connect(db_path) as conn:
        conn.execute("DELETE FROM ratings WHERE book_id = ?", (book_id,))
        conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
        tidy(conn)


def tidy(conn: sqlite3.Connection) -> None:
    """Keep the database clean after edits.

    - genres that differ only in capitalization ("Sci-Fi" / "Sci-FI") are merged into the
      spelling most books use
    - authors, genres, and ratings that no longer belong to any book are removed
    - http cover links are upgraded to https so phones and browsers don't block them
    """
    dupes = conn.execute(
        "SELECT lower(name) FROM genres GROUP BY lower(name) HAVING COUNT(*) > 1"
    ).fetchall()
    for (lowered,) in dupes:
        ranked = conn.execute(
            """SELECT g.id, COUNT(b.id) AS n FROM genres g LEFT JOIN books b ON b.genre_id = g.id
               WHERE lower(g.name) = ? GROUP BY g.id ORDER BY n DESC, g.id""",
            (lowered,),
        ).fetchall()
        keep = ranked[0][0]
        for genre_id, _ in ranked[1:]:
            conn.execute("UPDATE books SET genre_id = ? WHERE genre_id = ?", (keep, genre_id))
            conn.execute("DELETE FROM genres WHERE id = ?", (genre_id,))

    conn.execute("DELETE FROM ratings WHERE book_id NOT IN (SELECT id FROM books)")
    conn.execute("DELETE FROM authors WHERE id NOT IN (SELECT author_id FROM books WHERE author_id IS NOT NULL)")
    conn.execute("DELETE FROM genres WHERE id NOT IN (SELECT genre_id FROM books WHERE genre_id IS NOT NULL)")
    conn.execute("UPDATE books SET cover_url = 'https://' || substr(cover_url, 8) WHERE cover_url LIKE 'http://%'")


def prepare_database(db_path: Optional[str] = None) -> None:
    """Run once at startup: add missing indexes and tidy up older data."""
    with connect(db_path) as conn:
        conn.executescript(INDEXES)
        tidy(conn)


def openlibrary_link(title: str, author: str, isbn: Optional[str]) -> str:
    if isbn and str(isbn).strip():
        return f"https://openlibrary.org/isbn/{str(isbn).strip()}"
    query = " ".join(x for x in [(title or "").strip(), (author or "").strip()] if x)
    return f"https://openlibrary.org/search?q={quote_plus(query)}"
