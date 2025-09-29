import streamlit as st
import pandas as pd
from app import db_utils

GOLD = "#d4af37"

# =====================
# Shared CSS Styling
# =====================
def inject_custom_css():
    st.markdown(
        f"""
        <style>
            /* ===== Top Header (stone texture) ===== */
            header[data-testid="stHeader"] {{
                background-color: #555 !important;
                background-image: url("https://www.transparenttextures.com/patterns/stone-wall.png");
                background-size: cover;
                color: white;
            }}

            /* ===== Sidebar Doors ===== */
            section[data-testid="stSidebar"] {{
                background-color: #2a1d14;
                background-image: url("https://www.transparenttextures.com/patterns/dark-wood.png");
                background-size: cover;
            }}

            .sidebar-door {{
                display: block;
                padding: 16px;
                margin: 10px 0;
                border-radius: 8px;
                font-weight: bold;
                font-size: clamp(0.9em, 2vw, 1.1em);
                text-align: center;
                cursor: pointer;
                background-color: #555;
                color: white;
                transition: all 0.3s ease-in-out;
            }}
            .sidebar-door:hover {{
                background-color: #777;
                color: {GOLD};
                box-shadow: 0 0 14px {GOLD};
            }}
            .sidebar-door.active {{
                background-color: black !important;
                color: {GOLD} !important;
                box-shadow: 0 0 16px {GOLD};
            }}

            /* ===== KPI Boxes ===== */
            .gold-metric {{
                background: linear-gradient(135deg, #fff8dc, {GOLD}, #b8860b, #ffd700, #daa520);
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
            }}
            .gold-metric:hover {{
                box-shadow: 0 0 24px rgba(255, 255, 210, 1),
                            0 12px 28px rgba(218, 165, 32, 0.85),
                            inset 0 0 26px rgba(255, 250, 200, 0.95);
                transform: translateY(-4px) scale(1.02);
            }}
            .gold-metric h3 {{
                color: white !important;
                margin: 4px 0;
                font-size: 1.1em;
            }}
            .gold-metric p {{
                color: white !important;
                margin: 4px 0;
                font-size: 1.8em;
                font-weight: bold;
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
        active_class = "active" if st.session_state["page"] == page else ""
        if st.sidebar.markdown(
            f'<div class="sidebar-door {active_class}" onclick="window.location.reload();">{page}</div>',
            unsafe_allow_html=True,
        ):
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
        st.markdown(f"<div class='gold-metric'><h3>Total Books</h3><p>{total_books}</p></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='gold-metric'><h3>Avg. Rating</h3><p>{avg_rating}</p></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='gold-metric'><h3>Most Popular Genre</h3><p>{most_genre}</p></div>", unsafe_allow_html=True)
    with c4:
        st.markdown(f"<div class='gold-metric'><h3>Years Covered</h3><p>{years_covered}</p></div>", unsafe_allow_html=True)

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
                        <div class="corner-top-right"></div>
                        <div class="corner-bottom-left"></div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        st.info("No books yet — add your first one below!")
