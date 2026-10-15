"""Plain functions over the books table (no Streamlit), so they're easy to test."""
from typing import Iterable, Optional

import pandas as pd

QUOTES = [
    ("The darker the night, the brighter the stars.", "Fyodor Dostoevsky"),
    ("Blessed are the hearts that can bend; they shall never be broken.", "Albert Camus"),
    ("He who has a why to live can bear almost any how.", "Viktor Frankl"),
    ("The only way to deal with fear is to face it head on.", "Haruki Murakami"),
    ("The more sand has escaped from the hourglass of our life, the clearer we should see through it.", "Niccolò Machiavelli"),
    ("In order to write about life, first you must live it.", "Ernest Hemingway"),
    ("If you are always trying to be normal, you will never know how amazing you can be.", "Maya Angelou"),
    ("Freeing yourself was one thing, claiming ownership of that freed self was another.", "Toni Morrison"),
    ("The world is before you, and you need not take it or leave it as it was when you came in.", "James Baldwin"),
    ("A mind that is stretched by a new experience can never go back to its old dimensions.", "Oliver Wendell Holmes"),
]

SORTS = {
    "Recently read": (["year", "id"], [False, False]),
    "Highest rated": (["rating", "title"], [False, True]),
    "Title A–Z": (["title"], [True]),
    "Author A–Z": (["author", "title"], [True, True]),
}


def filter_books(df: pd.DataFrame, query: str = "", genres: Optional[Iterable[str]] = None,
                 years: Optional[Iterable[int]] = None, min_rating: float = 0.0) -> pd.DataFrame:
    """Books matching a title/author search (plain text, not a regex) and the chosen filters."""
    result = df
    query = (query or "").strip()
    if query:
        matches = (result["title"].str.contains(query, case=False, regex=False, na=False)
                   | result["author"].str.contains(query, case=False, regex=False, na=False))
        result = result[matches]
    if genres:
        result = result[result["genre"].isin(list(genres))]
    if years:
        result = result[result["year"].isin([int(y) for y in years])]
    if min_rating:
        result = result[result["rating"].fillna(0) >= min_rating]
    return result


def sort_books(df: pd.DataFrame, how: str) -> pd.DataFrame:
    columns, ascending = SORTS[how]
    return df.sort_values(columns, ascending=ascending, na_position="last")


def summary(df: pd.DataFrame) -> dict:
    """Headline numbers for the home page."""
    years = df["year"].dropna().astype(int)
    genres = df["genre"].dropna()
    return {
        "books": len(df),
        "average_rating": round(float(df["rating"].mean()), 2) if df["rating"].notna().any() else None,
        "top_genre": genres.mode().iloc[0] if not genres.empty else None,
        "latest_year": int(years.max()) if not years.empty else None,
        "latest_year_books": int((years == years.max()).sum()) if not years.empty else 0,
        "first_year": int(years.min()) if not years.empty else None,
        "five_star": int((df["rating"] >= 4.75).sum()),
    }


def stars(rating) -> str:
    """4.3 -> '★★★★☆ 4.3' (rounded to the nearest whole star)."""
    if rating is None or pd.isna(rating):
        return "Not rated"
    full = int(round(float(rating)))
    return "★" * full + "☆" * (5 - full) + f" {float(rating):.1f}"
