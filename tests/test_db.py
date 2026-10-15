import sqlite3

import numpy as np

from app import db_utils


def test_get_books_returns_every_book_with_a_rating(db_path):
    books = db_utils.get_books(db_path)
    assert len(books) > 0
    assert books["rating"].notna().all()
    assert {"title", "author", "genre", "year", "cover_url"} <= set(books.columns)


def test_add_edit_and_remove_a_book(empty_db):
    book_id = db_utils.add_book("Dune", "Frank Herbert", "Sci-Fi", 2024, 4.6, db_path=empty_db)
    books = db_utils.get_books(empty_db)
    assert books.loc[0, "title"] == "Dune" and books.loc[0, "rating"] == 4.6

    db_utils.update_book(book_id, "Dune Messiah", "Frank Herbert", "Sci-Fi", 2025, 4.0, db_path=empty_db)
    books = db_utils.get_books(empty_db)
    assert books.loc[0, "title"] == "Dune Messiah" and books.loc[0, "rating"] == 4.0

    db_utils.delete_book(book_id, db_path=empty_db)
    assert db_utils.get_books(empty_db).empty


def test_numpy_ids_are_stored_as_numbers(empty_db):
    book_id = db_utils.add_book("Beloved", "Toni Morrison", "Fiction", 2024, 5.0, db_path=empty_db)
    db_utils.update_book(np.int64(book_id), "Beloved", "Toni Morrison", "Fiction", 2024, 4.9, db_path=empty_db)
    with sqlite3.connect(empty_db) as conn:
        assert conn.execute("SELECT typeof(book_id) FROM ratings").fetchall() == [("integer",)]


def test_genres_ignore_capitalization(empty_db):
    db_utils.add_book("A", "X", "Sci-Fi", 2024, 4, db_path=empty_db)
    db_utils.add_book("B", "Y", "sci-fi", 2024, 4, db_path=empty_db)
    with sqlite3.connect(empty_db) as conn:
        assert conn.execute("SELECT name FROM genres").fetchall() == [("Sci-Fi",)]


def test_tidy_merges_genres_and_removes_leftovers(empty_db):
    with sqlite3.connect(empty_db) as conn:
        conn.executescript("""
            INSERT INTO authors (name) VALUES ('Kept'), ('Orphan');
            INSERT INTO genres (name) VALUES ('Sci-Fi'), ('Sci-FI'), ('Unused');
            INSERT INTO books (title, author_id, genre_id, year, cover_url) VALUES
                ('One', 1, 1, 2024, 'http://books.google.com/x'), ('Two', 1, 1, 2024, NULL), ('Three', 1, 2, 2024, NULL);
            INSERT INTO ratings (book_id, rating) VALUES (1, 4), (99, 3);
        """)
    db_utils.prepare_database(empty_db)
    with sqlite3.connect(empty_db) as conn:
        assert conn.execute("SELECT name FROM genres").fetchall() == [("Sci-Fi",)]
        assert conn.execute("SELECT name FROM authors").fetchall() == [("Kept",)]
        assert conn.execute("SELECT book_id FROM ratings").fetchall() == [(1,)]
        assert conn.execute("SELECT cover_url FROM books WHERE id = 1").fetchone() == ("https://books.google.com/x",)
        indexes = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type = 'index'")}
        assert "idx_books_genre" in indexes


def test_openlibrary_link_prefers_isbn():
    assert db_utils.openlibrary_link("Dune", "Herbert", "123") == "https://openlibrary.org/isbn/123"
    assert db_utils.openlibrary_link("Dune", "Frank Herbert", None) == "https://openlibrary.org/search?q=Dune+Frank+Herbert"
