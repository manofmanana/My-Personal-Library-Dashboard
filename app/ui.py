import streamlit as st
import pandas as pd
from app import db_utils

# 🎨 Theme colors
FOREST_GREEN = "#2e4e3f"
FOREST_GREEN_DARK = "#1c3b2a"
PARCHMENT = "#dcd3b2"

# =====================
# Shared CSS Styling
# =====================
def inject_custom_css():
    st.markdown(
        f"""
        <style>
            /* ===== Top Header ===== */
            header[data-testid="stHeader"] {{
                background-color: #555 !important;
                background-image: url("https://www.transparenttextures.com/patterns/stone-wall.png");
                background-size: cover;
                color: white;
            }}

            /* ===== Sidebar ===== */
            section[data-testid="stSidebar"] {{
                background-color: #2a1d14;
                background-image: url("https://www.transparenttextures.com/patterns/dark-wood.png");
                background-size: cover;
            }}

            /* Sidebar title */
            .stSidebar h1 {{
                color: white !important;
                font-weight: bold !important;
                text-shadow: 1px 1px 3px rgba(0,0,0,0.6);
            }}

            /* Sidebar buttons */
            .stSidebar .stButton > button {{
                background-color: {FOREST_GREEN} !important;
                color: white !important;
                border-radius: 6px;
                padding: 0.6em 1em;
                font-weight: bold;
                border: none;
                width: 100%;
            }}
            .stSidebar .stButton > button:hover {{
                background-color: #3d6f56 !important;
                color: white !important;
                box-shadow: 0 0 10px {FOREST_GREEN};
            }}

            /* ===== KPI Boxes ===== */
            .green-metric {{
                background: linear-gradient(135deg, {FOREST_GREEN}, {FOREST_GREEN_DARK});
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
                box-shadow: 0 0 24px {FOREST_GREEN},
                            0 12px 28px rgba(46, 78, 63, 0.85),
                            inset 0 0 26px rgba(46, 78, 63, 0.95);
                transform: translateY(-4px) scale(1.02);
            }}
            .green-metric h3, .green-metric p {{
                color: white !important;
            }}

            /* ===== Buttons ===== */
            button, .stDownloadButton button, .stButton button {{
                background-color: {FOREST_GREEN} !important;
                color: white !important;
                border: none !important;
                border-radius: 6px !important;
                padding: 8px 16px !important;
                font-weight: bold !important;
                transition: all 0.2s ease-in-out !important;
            }}
            button:hover, .stDownloadButton button:hover, .stButton button:hover {{
                background-color: {FOREST_GREEN_DARK} !important;
                color: white !important;
                box-shadow: 0 0 10px {FOREST_GREEN};
            }}

            /* ===== Inputs & Selectboxes ===== */
            .stTextInput > div > div > input,
            .stTextArea > div > textarea,
            .stSelectbox > div > div,
            .stNumberInput > div > input,
            .stPasswordInput > div > input {{
                background-color: white !important;
                color: black !important;
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

            /* ===== Expanders ===== */
            div.streamlit-expanderHeader {{
                background-color: {FOREST_GREEN} !important;
                color: white !important;
                font-weight: bold !important;
                border-radius: 6px !important;
            }}
            .streamlit-expanderContent {{
                background-color: {PARCHMENT} !important;
                border-left: 3px solid {FOREST_GREEN};
                padding: 12px;
                color: black !important;
            }}

            /* ===== Book Covers ===== */
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
                border: 12px solid {FOREST_GREEN};
                box-shadow:
                    0 0 12px rgba(46, 78, 63, 0.8),
                    0 6px 16px rgba(0, 0, 0, 0.7);
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

            /* ===== Overlay on book covers ===== */
            .book-overlay {{
                position: absolute;
                top: 0; left: 0;
                width: 100%; height: 100%;
                background: rgba(0,0,0,0.6);
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
        </style>
        """,
        unsafe_allow_html=True,
    )

# =====================
# Sidebar Doors Navigation
# =====================
def show_sidebar_doors(pages):
    st.sidebar.title("Hallway")

    if "page" not in st.session_state:
        st.session_state["page"] = pages[0]

    for page in pages:
        if st.sidebar.button(page, use_container_width=True):
            st.session_state["page"] = page

    return st.session_state["page"]

# =====================
# KPIs
# =====================
def show_kpis(df: pd.DataFrame):
    total_books = len(df)
    avg_rating = f"{df['rating'].mean():.2f}" if total_books > 0 else "0.00"
    most_genre = df["genre"].mode()[0] if total_books > 0 and not df["genre"].dropna().empty else "N/A"
    years_covered = (
        f"{int(df['year'].min())}–{int(df['year'].max())}" if total_books > 0 and df["year"].notna().any() else "N/A"
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"<div class='green-metric'><h3>Total Books</h3><p>{total_books}</p></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='green-metric'><h3>Avg. Rating</h3><p>{avg_rating}</p></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='green-metric'><h3>Most Popular Genre</h3><p>{most_genre}</p></div>", unsafe_allow_html=True)
    with c4:
        st.markdown(f"<div class='green-metric'><h3>Years Covered</h3><p>{years_covered}</p></div>", unsafe_allow_html=True)

# =====================
# Book Grid
# =====================
def show_book_grid(df: pd.DataFrame):
    st.subheader("Bookstacks")

    if not df.empty:
        cols = st.columns(5, gap="small")
        for i, (_, row) in enumerate(df.iterrows()):
            with cols[i % 5]:
                cover_url = db_utils.get_or_fetch_cover_for_row(row)
                link = db_utils.openlibrary_link(row.get("title"), row.get("author"), row.get("isbn"))
                rating = row.get("rating", "N/A")
                genre = row.get("genre", "Unknown")

                st.markdown(
                    f"""
                    <div class="book-cover">
                        <a href="{link}" target="_blank" class="book-link">
                            <img src="{cover_url}" alt="cover"/>
                            <div class="book-overlay">
                                <div style="font-size:1.1em; font-weight:bold;">{rating}/5</div>
                                <div style="font-size:1em; margin-top:4px;">{genre}</div>
                            </div>
                        </a>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        st.info("No books yet — add your first one below!")
