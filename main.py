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
# CSS Styling
# =====================
st.markdown(
    f"""
    <style>
        body, .stApp {{
            background-color: {PARCHMENT};
            color: #1c1c1c;
        }}
        section[data-testid="stSidebar"] {{
            background-color: {MID_BROWN};
            background-image: url("https://www.transparenttextures.com/patterns/dark-wood.png");
            background-size: cover;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: #2e4e3f !important;
        }}

        /* === Hallway title in sidebar === */
        .css-1d391kg, .sidebar-title, .stSidebar h1 {{
            color: white !important;
            font-weight: bold !important;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.6);
        }}

        /* === Banner text force white === */
        .banner-title {{
            color: white !important;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.7);
        }}
        .banner-subtitle {{
            color: white !important;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.6);
        }}

        /* === Sidebar Buttons (Forest Green) === */
        .stButton > button, .stDownloadButton > button {{
            background-color: {FOREST_GREEN} !important;
            color: white !important;
            border-radius: 6px;
            padding: 0.5em 1em;
            font-weight: bold;
            border: none;
        }}
        .stButton > button:hover, .stDownloadButton > button:hover {{
            background-color: #3d6f56 !important;
            color: white !important;
            box-shadow: 0 0 10px {FOREST_GREEN};
        }}

        /* === Inputs & Selectboxes (better visibility) === */
        .stTextInput > div > div > input,
        .stTextArea > div > textarea,
        .stSelectbox > div > div,
        .stNumberInput > div > input,
        .stPasswordInput > div > input {{
            background-color: #f7f3e9 !important;
            color: #1c1c1c !important;
            border: 1px solid {FOREST_GREEN} !important;
            border-radius: 6px;
            padding: 6px;
        }}
        .stTextInput > div > div > input:focus,
        .stTextArea > div > textarea:focus,
        .stSelectbox > div > div:focus,
        .stNumberInput > div > input:focus,
        .stPasswordInput > div > input:focus {{
            outline: none !important;
            border: 2px solid {FOREST_GREEN} !important;
            box-shadow: 0 0 6px {FOREST_GREEN};
        }}

        /* === Sidebar Bookworm image (pushed lower) === */
        .sidebar-bookworm {{
            display: flex;
            justify-content: center;
            align-items: center;
            margin-top: 350px; /* pushes it way down */
            padding: 40px 0;
        }}
        .sidebar-bookworm img {{
            max-width: 120px;
            height: auto;
        }}

        /* === Book Covers with forest green frames === */
        .book-cover {{
            margin-bottom: 14px;
            position: relative;
            display: inline-block;
            overflow: visible;
        }}
        .book-cover img {{
            width: 100%;
            height: auto;
            max-height: 400px;
            object-fit: contain;
            border-radius: 8px;
            border: 14px solid transparent;
            border-image: linear-gradient(135deg, #e6ddc5, {FOREST_GREEN}, #1c3b2a) 1;
            box-shadow:
                0 0 12px rgba(30, 60, 40, 0.6),
                0 6px 16px rgba(0, 0, 0, 0.7),
                inset 0 0 18px rgba(40, 80, 55, 0.6),
                inset 2px 2px 8px rgba(0,0,0,0.5);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        .book-cover:hover img {{
            transform: translateY(-6px) scale(1.05);
            box-shadow:
                0 0 24px rgba(46, 78, 63, 1),
                0 12px 28px rgba(46, 78, 63, 0.85),
                inset 0 0 26px rgba(46, 78, 63, 0.95);
            cursor: pointer;
        }}

        /* Floating decorative corners */
        .book-cover::before,
        .book-cover::after,
        .book-cover .corner-top-right,
        .book-cover .corner-bottom-left {{
            content: "";
            position: absolute;
            width: 28px;
            height: 28px;
            border: 4px solid {FOREST_GREEN};
            filter: drop-shadow(0 0 6px rgba(46, 78, 63, 0.9));
            pointer-events: none;
        }}
        .book-cover::before {{
            top: -10px; left: -10px;
            border-right: none; border-bottom: none;
            border-radius: 12px 0 0 0;
        }}
        .book-cover::after {{
            bottom: -10px; right: -10px;
            border-left: none; border-top: none;
            border-radius: 0 0 12px 0;
        }}
        .book-cover .corner-top-right {{
            top: -10px; right: -10px;
            border-left: none; border-bottom: none;
            border-radius: 0 12px 0 0;
        }}
        .book-cover .corner-bottom-left {{
            bottom: -10px; left: -10px;
            border-right: none; border-top: none;
            border-radius: 0 0 0 12px;
        }}

        /* === Overlay with rating and genre === */
        .book-overlay {{
            position: absolute;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background: rgba(0,0,0,0.7);
            color: white;
            font-family: 'Georgia', serif;
            font-size: 0.9em;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            opacity: 0;
            transition: opacity 0.3s ease;
            border-radius: 8px;
        }}
        .book-cover:hover .book-overlay {{
            opacity: 1;
        }}

        /* === KPI Boxes Styling (forest green, white text) === */
        .green-metric {{
            background: linear-gradient(135deg, #2e4e3f, #1c3b2a);
            border-radius: 14px;
            padding: 18px;
            margin: 6px;
            text-align: center;
            box-shadow: 0 6px 16px rgba(0,0,0,0.6);
            transition: all 0.3s ease-in-out;
            height: 140px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            color: white !important;
        }}
        .green-metric:hover {{
            box-shadow: 0 0 24px rgba(46, 78, 63, 1),
                        0 12px 28px rgba(46, 78, 63, 0.85),
                        inset 0 0 26px rgba(46, 78, 63, 0.95);
            transform: translateY(-4px) scale(1.02);
        }}
        .green-metric h3 {{
            color: white !important;
            margin: 4px 0;
            font-size: 1.1em;
        }}
        .green-metric p {{
            color: white !important;
            margin: 4px 0;
            font-size: 1.8em;
            font-weight: bold;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

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
                        A dashboard tracking my reading journey across years, genres, and ideas.
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
        f"<div style='background:{FOREST_GREEN}; color:white; padding:15px; border-radius:12px; margin:20px 0; text-align:center; font-size:1.1em; font-weight:bold;'>{quote} — {author}</div>",
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='green-metric'><h3>Total Books</h3><p>{len(df)}</p></div>", unsafe_allow_html=True)
    with col2:
        avg_rating = round(df['rating'].mean(), 2) if not df.empty else "N/A"
        st.markdown(f"<div class='green-metric'><h3>Avg. Rating</h3><p>{avg_rating}</p></div>", unsafe_allow_html=True)
    with col3:
        most_popular_genre = df['genre'].mode()[0] if not df.empty and not df['genre'].dropna().empty else "N/A"
        st.markdown(f"<div class='green-metric'><h3>Most Popular Genre</h3><p>{most_popular_genre}</p></div>", unsafe_allow_html=True)
    with col4:
        if not df.empty:
            min_year, max_year = int(df['year'].min()), int(df['year'].max())
            years_range = f"{min_year}–{max_year}"
        else:
            years_range = "N/A"
        st.markdown(f"<div class='green-metric'><h3>Years Covered</h3><p>{years_range}</p></div>", unsafe_allow_html=True)

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
