import pandas as pd

from app.covers import look_up_book
from app.library import filter_books, sort_books, stars, summary

BOOKS = pd.DataFrame([
    {"id": 1, "title": "Dune (Deluxe)", "author": "Frank Herbert", "genre": "Sci-Fi", "year": 2024, "rating": 4.8},
    {"id": 2, "title": "Beloved", "author": "Toni Morrison", "genre": "Fiction", "year": 2025, "rating": 4.2},
    {"id": 3, "title": "Meditations", "author": "Marcus Aurelius", "genre": "Philosophy", "year": 2025, "rating": None},
])


def test_search_is_plain_text_not_a_pattern():
    # "(" used to crash the search because it was treated as a regular expression
    assert list(filter_books(BOOKS, "(deluxe")["id"]) == [1]
    assert list(filter_books(BOOKS, "morrison")["id"]) == [2]


def test_filters_combine():
    assert list(filter_books(BOOKS, genres=["Fiction", "Philosophy"], years=[2025])["id"]) == [2, 3]
    assert list(filter_books(BOOKS, min_rating=4.5)["id"]) == [1]


def test_sorting():
    assert list(sort_books(BOOKS, "Highest rated")["id"]) == [1, 2, 3]
    assert list(sort_books(BOOKS, "Title A–Z")["title"]) == ["Beloved", "Dune (Deluxe)", "Meditations"]


def test_summary():
    s = summary(BOOKS)
    assert s == {"books": 3, "average_rating": 4.5, "top_genre": "Fiction", "latest_year": 2025,
                 "latest_year_books": 2, "first_year": 2024, "five_star": 1}


def test_stars():
    assert stars(4.3) == "★★★★☆ 4.3"
    assert stars(None) == "Not rated"


def test_cover_lookup_survives_no_internet(monkeypatch):
    import requests

    def offline(*args, **kwargs):
        raise requests.ConnectionError("offline")

    monkeypatch.setattr(requests, "get", offline)
    assert look_up_book("Dune", "Frank Herbert") == {"cover_url": None, "isbn": None, "subjects": None}
