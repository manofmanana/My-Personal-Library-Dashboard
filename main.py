import streamlit as st
import base64
import os
import random
import pandas as pd
from dotenv import load_dotenv
import app.db_utils as db_utils
import app.ui as ui
import app.analytics as analytics

# =====================
# Load environment variables
# =====================
load_dotenv()
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "JulietA")  # fallback if not set

# =====================
# App/Theme Settings
# =====================
st.set_page_config(
    page_title="Alejandro's Library",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🎨 Colors
DARK_BROWN = "#3b2a20"    # sidebar dark brown
MID_BROWN = "#2a1d14"     # deeper sidebar accent
FOREST_GREEN = "#2e4e3f"  # main accent
PARCHMENT = "#e6ddc5"     # parchment ivory background

# =====================
# Inject CSS (moved to ui.py)
# =====================
ui.inject_custom_css()

# =====================
# Data
# =====================
df = db_utils.get_books()

# =====================
# Sidebar Navigation
# =====================
st.sidebar.title("Hallway")

PAGES = ["Library", "Computer Lab Dashboard", "Bookstacks", "Stack Maintenance"]

selected_page = None
for page in PAGES:
    if st.sidebar.button(page, key=page, help=f"Enter {page}", use_container_width=True):
        st.session_state["page"] = page
        selected_page = page

if "page" not in st.session_state:
    st.session_state["page"] = "Library"

page = selected_page or st.session_state["page"]

# Bookworm image
bookworm_path = "bookworm.png"
if os.path.exists(bookworm_path):
    with open(bookworm_path, "rb") as f:
        worm_bytes = f.read()
    worm_base64 = base64.b64encode(worm_bytes).decode()
    st.sidebar.markdown(
        f"""
        <div class="sidebar-bookworm">
            <img src="data:image/png;base64,{worm_base64}" alt="Bookworm"/>
        </div>
        """,
        unsafe_allow_html=True
    )

# =====================
# Page: Library
# =====================
if page == "Library":
    banner_path = "banner.JPG"
    if os.path.exists(banner_path):
        with open(banner_path, "rb") as f:
            banner_bytes = f.read()
        banner_base64 = base64.b64encode(banner_bytes).decode()
        st.markdown(
            f"""
            <div style="position: relative; width: 100%; overflow: hidden;">
                <img src="data:image/jpg;base64,{banner_base64}"
                    style="width:100%; height:auto; border-radius: 0 0 12px 12px; filter: brightness(60%);">
                <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
                            text-align: center; padding: 0 20px;">
                    <h1 class="banner-title" style="font-size: clamp(1.5em, 4vw, 3em); margin-bottom: 0.3em;">
                        Alejandro's Library
                    </h1>
                    <p class="banner-subtitle" style="font-size: clamp(0.9em, 2vw, 1.2em); margin: 0;">
                        Dashboard tracking my reading journey across years, genres, and ideas.
                    </p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    quotes = [
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
    quote, author = random.choice(quotes)
    st.markdown(
        f"<div style='background:{ui.KPI_BROWN}; color:white; padding:15px; border-radius:12px; margin:20px 0; text-align:center; font-size:1.1em; font-weight:bold;'>{quote} — {author}</div>",
        unsafe_allow_html=True
    )

    ui.show_kpis(df)

# =====================
# Page: Computer Lab Dashboard
# =====================
elif page == "Computer Lab Dashboard":
    analytics.show_charts(df)

# =====================
# Page: Bookstacks
# =====================
elif page == "Bookstacks":
    filtered_df = df.copy()
    with st.expander("Filter Books", expanded=False):
        search_query = st.text_input("Search by title or author")
        genres = sorted(df["genre"].dropna().unique())
        genre_filter = st.selectbox("Filter by genre", ["All"] + genres)
        if not df["year"].dropna().empty:
            years = sorted(df["year"].dropna().unique())
            year_filter = st.selectbox("Filter by year", ["All"] + [str(y) for y in years])
        else:
            year_filter = "All"

        if search_query:
            filtered_df = filtered_df[
                filtered_df["title"].str.contains(search_query, case=False) |
                filtered_df["author"].str.contains(search_query, case=False)
            ]
        if genre_filter != "All":
            filtered_df = filtered_df[filtered_df["genre"] == genre_filter]
        if year_filter != "All":
            filtered_df = filtered_df[filtered_df["year"].astype(str) == year_filter]

    ui.show_book_grid(filtered_df)

    if not filtered_df.empty:
        st.subheader("Export Bookstack Data")
        st.download_button(
            "Download Filtered Bookstack as CSV",
            filtered_df.to_csv(index=False).encode("utf-8"),
            "bookstacks_filtered.csv",
            "text/csv"
        )

# =====================
# Page: Stack Maintenance
# =====================
elif page == "Stack Maintenance":
    st.subheader("Manage Stacks")
    password = st.text_input("Enter password to manage book stacks:", type="password")

    if password == ADMIN_PASSWORD:
        tab_add, tab_edit, tab_delete = st.tabs(["Add Book", "Edit Book", "Delete Book"])

        # ---- ADD ----
        with tab_add:
            with st.form("add_book_form", clear_on_submit=True):
                title = st.text_input("Book Title")
                author = st.text_input("Author(s)")
                year = st.number_input("Year Read", min_value=0, max_value=2100, value=2025)
                rating = st.slider("Rating", 0.0, 5.0, value=0.0, step=0.1)
                genre = st.text_input("Genre")
                isbn = st.text_input("ISBN (optional)")
                subjects = st.text_area("Subjects (optional)")
                cover_url = st.text_input("Cover URL (optional)")

                if st.form_submit_button("Add Book"):
                    try:
                        fetched = db_utils.fetch_book_data(title.strip(), author.strip(), isbn.strip() or None)
                        cover_final = cover_url.strip() or fetched.get("cover_url")
                        isbn_final = isbn.strip() or fetched.get("isbn")
                        subjects_final = subjects.strip() or fetched.get("subjects")

                        db_utils.add_book(
                            title=title.strip(),
                            author=author.strip(),
                            genre=genre.strip(),
                            year=int(year),
                            rating=float(rating),
                            isbn=isbn_final,
                            subjects=subjects_final,
                            cover_url=cover_final,
                        )
                        st.success(f"Book '{title}' submitted successfully.")
                        st.rerun()
                    except Exception as e:
                        st.error("Could not add book.")
                        st.exception(e)

        # ---- EDIT ----
        with tab_edit:
            if df.empty:
                st.info("No books available to edit.")
            else:
                def book_label(row):
                    year = int(row["year"]) if pd.notna(row["year"]) else "—"
                    return f'#{int(row["id"])} — {row["title"]} by {row["author"]} ({year})'

                options = {book_label(r): int(r["id"]) for _, r in df.iterrows()}
                selected_label = st.selectbox("Select a book to edit", list(options.keys()))
                selected_id = options[selected_label]
                book_row = df[df["id"] == selected_id].iloc[0]

                with st.form("edit_book_form"):
                    title = st.text_input("Edit Title", value=book_row["title"])
                    author = st.text_input("Edit Author(s)", value=book_row["author"])
                    year = st.number_input("Edit Year Read", min_value=0, max_value=2100, value=int(book_row["year"]))
                    rating = st.slider("Edit Rating", 0.0, 5.0, value=float(book_row["rating"]), step=0.1)
                    genre = st.text_input("Edit Genre", value=book_row["genre"])
                    isbn = st.text_input("Edit ISBN (optional)", value=book_row["isbn"] or "")
                    subjects = st.text_area("Edit Subjects (optional)", value=book_row["subjects"] or "")
                    cover_url = st.text_input("Edit Cover URL (optional)", value=book_row["cover_url"] or "")

                    if st.form_submit_button("Save Changes"):
                        try:
                            fetched = db_utils.fetch_book_data(title.strip(), author.strip(), isbn.strip() or None)
                            cover_final = cover_url.strip() or fetched.get("cover_url")
                            isbn_final = isbn.strip() or fetched.get("isbn")
                            subjects_final = subjects.strip() or fetched.get("subjects")

                            db_utils.update_book(
                                book_id=selected_id,
                                title=title.strip(),
                                author=author.strip(),
                                genre=genre.strip(),
                                year=int(year),
                                rating=float(rating),
                                isbn=isbn_final,
                                subjects=subjects_final,
                                cover_url=cover_final,
                            )
                            st.success(f"Book '{title}' updated successfully.")
                            st.rerun()
                        except Exception as e:
                            st.error("Could not save changes.")
                            st.exception(e)

        # ---- DELETE ----
        with tab_delete:
            if df.empty:
                st.info("No books available to delete.")
            else:
                def book_label_del(row):
                    year = int(row["year"]) if pd.notna(row["year"]) else "—"
                    return f'#{int(row["id"])} — {row["title"]} by {row["author"]} ({year})'

                options_del = {book_label_del(r): int(r["id"]) for _, r in df.iterrows()}
                selected_label_del = st.selectbox("Select a book to delete", list(options_del.keys()))

                if st.button("Confirm Delete"):
                    try:
                        db_utils.delete_book(options_del[selected_label_del])
                        st.warning("Book deleted successfully.")
                        st.rerun()
                    except Exception as e:
                        st.error("Could not delete book.")
                        st.exception(e)

    else:
        if password:
            st.error("Incorrect password")
