"""The app's four pages."""
import hmac
import os
import random

import pandas as pd
import plotly.express as px
import streamlit as st

from app import db_utils, theme
from app.covers import look_up_book
from app.library import QUOTES, SORTS, filter_books, sort_books, summary


@st.cache_data(show_spinner=False)
def load_books() -> pd.DataFrame:
    return db_utils.get_books()


def books_changed(message: str):
    """After an edit: refresh the cached books and show a toast that survives the rerun."""
    load_books.clear()
    st.session_state["flash"] = message
    st.rerun()


def show_flash():
    message = st.session_state.pop("flash", None)
    if message:
        st.toast(message, icon="📚")


# ---------- Library (home) ----------

def home():
    df = load_books()
    s = summary(df)
    theme.hero("Welcome to", "Alejandro's Library",
               "A record of my reading journey across years, genres, and ideas.")
    theme.quote(*random.choice(QUOTES))
    theme.stat_cards([
        ("Books read", s["books"], f"since {s['first_year']}" if s["first_year"] else ""),
        ("Average rating", f"{s['average_rating']:.2f}" if s["average_rating"] else "–", "out of 5"),
        ("Favorite genre", s["top_genre"] or "–", "most read"),
        (f"Read in {s['latest_year']}" if s["latest_year"] else "Latest year", s["latest_year_books"], "my latest reading year"),
    ])

    st.subheader("Latest reads")
    theme.book_shelf(sort_books(df, "Recently read").head(12), db_utils.openlibrary_link, row=True)

    favorites = sort_books(df[df["rating"] >= 4.5], "Highest rated").head(12)
    if not favorites.empty:
        st.subheader("All-time favorites")
        theme.book_shelf(favorites, db_utils.openlibrary_link, row=True)

    col1, col2 = st.columns(2)
    col1.page_link(st.session_state["pages"]["shelf"], label="Browse every book", icon=":material/menu_book:")
    col2.page_link(st.session_state["pages"]["stats"], label="See the reading stats", icon=":material/insights:")


# ---------- Bookstacks ----------

def shelf():
    df = load_books()
    st.title("Bookstacks")
    st.markdown(f'<p class="section-note">All {len(df)} books, newest first. Tap a cover to look it up on Open Library.</p>',
                unsafe_allow_html=True)

    query = st.text_input("Search", placeholder="Search by title or author", label_visibility="collapsed",
                          key="shelf_query")
    with st.expander("Filter and sort", icon=":material/tune:"):
        genres = st.multiselect("Genres", sorted(df["genre"].dropna().unique()))
        years = st.pills("Year read", sorted(df["year"].dropna().astype(int).unique(), reverse=True),
                         selection_mode="multi")
        col1, col2 = st.columns(2)
        min_rating = col1.select_slider("Minimum rating", options=[0, 1, 2, 3, 3.5, 4, 4.5, 5], value=0)
        sort = col2.selectbox("Sort by", list(SORTS))

    shown = sort_books(filter_books(df, query, genres, years, min_rating), sort)
    if shown.empty:
        st.info("No books match those filters.")
        return
    if len(shown) < len(df):
        st.caption(f"Showing {len(shown)} of {len(df)} books")
    theme.book_shelf(shown, db_utils.openlibrary_link)

    st.download_button("Download these books as CSV", shown.to_csv(index=False).encode("utf-8"),
                       "alejandros_library.csv", "text/csv", icon=":material/download:")


# ---------- Computer Lab (stats) ----------

def stats():
    df = load_books()
    st.title("Computer Lab")
    st.markdown('<p class="section-note">The numbers behind the shelves.</p>', unsafe_allow_html=True)
    if df.empty:
        st.info("No books yet.")
        return
    books = df.assign(year=df["year"].astype("Int64"), genre=df["genre"].fillna("Unknown"))
    rated = books.dropna(subset=["rating"])

    left, right = st.columns(2, gap="large")
    with left:
        per_year = books.groupby("year").size().reset_index(name="books")
        per_year["year"] = per_year["year"].astype(str)  # years are labels, not numbers (no "2,021.5")
        fig = px.bar(per_year, x="year", y="books", text="books", title="Books per year")
        fig.update_traces(marker_color=theme.LEATHER, textposition="outside", cliponaxis=False)
        fig.update_layout(xaxis_title=None, yaxis_title=None, yaxis_visible=False)
        theme.chart(fig)
    with right:
        fig = px.histogram(rated, x="rating", nbins=10, title="How I rate books")
        fig.update_traces(marker_color="#d4a24c")
        fig.update_layout(xaxis_title="Rating", yaxis_title="Books", xaxis_range=[0, 5.2])
        theme.chart(fig)

    left, right = st.columns(2, gap="large")
    with left:
        per_genre = books.groupby("genre").size().sort_values().tail(10).reset_index(name="books")
        fig = px.bar(per_genre, x="books", y="genre", orientation="h", text="books", title="Top genres")
        fig.update_traces(marker_color="#5f7a4f", textposition="outside", cliponaxis=False)
        fig.update_layout(xaxis_visible=False, yaxis_title=None)
        theme.chart(fig, height=380)
    with right:
        by_genre = (rated.groupby("genre")["rating"].agg(["mean", "count"])
                    .query("count >= 2").sort_values("mean").tail(10).reset_index())
        fig = px.bar(by_genre, x="mean", y="genre", orientation="h", title="Best-rated genres",
                     text=by_genre["mean"].map(lambda r: f"{r:.2f}"), hover_data={"count": True})
        fig.update_traces(marker_color="#3d5a73", textposition="outside", cliponaxis=False)
        fig.update_layout(xaxis_range=[0, 5.6], xaxis_visible=False, yaxis_title=None)
        theme.chart(fig, height=380)
        st.caption("Genres with at least two books.")

    trend = rated.groupby("year")["rating"].mean().reset_index()
    if len(trend) > 1:
        trend["year"] = trend["year"].astype(str)
        fig = px.line(trend, x="year", y="rating", markers=True, title="Average rating by year")
        fig.update_traces(line_color=theme.LEATHER, line_width=3, marker_size=10)
        fig.update_layout(xaxis_title=None, yaxis_title=None, yaxis_range=[0, 5])
        theme.chart(fig, height=300)


# ---------- Stack Maintenance (admin) ----------

def admin_password():
    """From Streamlit secrets (on the cloud) or the environment / .env file (locally)."""
    try:
        from_secrets = st.secrets.get("ADMIN_PASSWORD")
    except Exception:  # no secrets file at all
        from_secrets = None
    return from_secrets or os.environ.get("ADMIN_PASSWORD")


def manage():
    st.title("Stack Maintenance")
    password = admin_password()
    if not password:
        st.info("Editing is turned off. Set ADMIN_PASSWORD in Streamlit secrets (or a .env file) to manage books.")
        return
    if not st.session_state.get("is_admin"):
        with st.form("login"):
            attempt = st.text_input("Password", type="password")
            if st.form_submit_button("Unlock", type="primary"):
                if hmac.compare_digest(attempt.encode(), password.encode()):
                    st.session_state["is_admin"] = True
                    st.rerun()
                st.error("Incorrect password.")
        return

    st.warning("On Streamlit Community Cloud, changes here last until the app restarts. "
               "To keep them for good, edit locally and commit books_normalized.db.", icon=":material/info:")
    df = load_books()
    add_tab, edit_tab, delete_tab = st.tabs(["Add a book", "Edit a book", "Remove a book"])

    with add_tab:
        with st.form("add_book", clear_on_submit=True):
            title = st.text_input("Title *")
            author = st.text_input("Author *")
            col1, col2 = st.columns(2)
            year = col1.number_input("Year read", min_value=1900, max_value=2100, value=pd.Timestamp.now().year)
            rating = col2.slider("Rating", 0.0, 5.0, 4.0, 0.1)
            genre = st.text_input("Genre", placeholder="Fiction, Memoir, Sci-Fi...")
            with st.expander("Optional details"):
                isbn = st.text_input("ISBN")
                cover_url = st.text_input("Cover image URL", help="Leave empty to look one up automatically.")
                subjects = st.text_area("Subjects")
            if st.form_submit_button("Add book", type="primary"):
                if not title.strip() or not author.strip():
                    st.error("Title and author are required.")
                else:
                    with st.spinner("Looking up the cover..."):
                        found = look_up_book(title.strip(), author.strip(), isbn) if not cover_url.strip() else {}
                    db_utils.add_book(title.strip(), author.strip(), genre.strip(), int(year), rating,
                                      isbn=isbn.strip() or found.get("isbn"),
                                      subjects=subjects.strip() or found.get("subjects"),
                                      cover_url=cover_url.strip() or found.get("cover_url"))
                    books_changed(f"Added “{title.strip()}”")

    labels = {f"{r.title} — {r.author} ({int(r.year) if pd.notna(r.year) else '?'})": int(r.id) for r in df.itertuples()}

    with edit_tab:
        if not labels:
            st.info("No books yet.")
        else:
            choice = st.selectbox("Book to edit", list(labels), key="edit_choice")
            book = df[df["id"] == labels[choice]].iloc[0]
            with st.form("edit_book"):
                title = st.text_input("Title", book["title"])
                author = st.text_input("Author", book["author"] or "")
                col1, col2 = st.columns(2)
                year = col1.number_input("Year read", 1900, 2100, int(book["year"]) if pd.notna(book["year"]) else pd.Timestamp.now().year)
                rating = col2.slider("Rating", 0.0, 5.0, float(book["rating"]) if pd.notna(book["rating"]) else 0.0, 0.1)
                genre = st.text_input("Genre", book["genre"] or "")
                isbn = st.text_input("ISBN", book["isbn"] or "")
                cover_url = st.text_input("Cover image URL", book["cover_url"] or "")
                subjects = st.text_area("Subjects", book["subjects"] or "")
                refetch = st.checkbox("Look up the cover again")
                if st.form_submit_button("Save changes", type="primary"):
                    found = look_up_book(title.strip(), author.strip(), isbn) if refetch else {}
                    db_utils.update_book(labels[choice], title.strip(), author.strip(), genre.strip(), int(year), rating,
                                         isbn=isbn.strip() or found.get("isbn") or None,
                                         subjects=subjects.strip() or found.get("subjects") or None,
                                         cover_url=found.get("cover_url") or cover_url.strip() or None)
                    books_changed(f"Saved “{title.strip()}”")

    with delete_tab:
        if not labels:
            st.info("No books yet.")
        else:
            choice = st.selectbox("Book to remove", list(labels), key="delete_choice")
            sure = st.checkbox(f"Yes, remove “{choice.split(' — ')[0]}” from the library")
            if st.button("Remove book", type="primary", disabled=not sure):
                db_utils.delete_book(labels[choice])
                books_changed("Book removed")

    if st.button("Lock", icon=":material/lock:"):
        st.session_state["is_admin"] = False
        st.rerun()
