import streamlit as st
import pandas as pd
from app import db_utils

# 🎨 Theme colors
KPI_BROWN = "#4b3a26"
KPI_BROWN_DARK = "#2f2419"
PARCHMENT = "#e6ddc5"

# =====================
# Shared CSS Styling
# =====================
def inject_custom_css():
    st.markdown(
        f"""
        <style>
            /* ===== Page Background with Gradient ===== */
            .stApp {{
                background: linear-gradient(135deg, #efdfbb, #c8b68f);
            }}

            /* ===== Top Header ===== */
            header[data-testid="stHeader"] {{
                background-color: #4b3a26 !important;
                background-image: url("https://www.transparenttextures.com/patterns/stone-wall.png");
                background-size: cover;
                color: white;
            }}

            /* ===== Dashboard Title ===== */
            .main-title {{
                text-align: center;
                font-size: 2.2em;
                font-weight: bold;
                margin-top: 10px;
                margin-bottom: 6px;
                color: {KPI_BROWN_DARK};
            }}
            .main-subtitle {{
                text-align: center;
                font-size: 1.1em;
                font-style: italic;
                margin-bottom: 30px;
                color: {KPI_BROWN};
            }}

            /* ===== Sidebar ===== */
            section[data-testid="stSidebar"] {{
                background-color: #2a1d14;
                background-image: url("https://www.transparenttextures.com/patterns/dark-wood.png");
                background-size: cover;
                display: flex;
                flex-direction: column;
                justify-content: flex-start;
            }}
            .stSidebar h1 {{
                color: white !important;
                font-weight: bold !important;
                text-shadow: 1px 1px 3px rgba(0,0,0,0.6);
            }}

            /* ===== Sidebar Bookworm Image ===== */
            .sidebar-bookworm {{
                margin-top: 350px; /* Lowered vertically */
                display: flex;
                justify-content: center;
                padding: 10px;
            }}
            .sidebar-bookworm img {{
                width: 120px;
                height: auto;
                opacity: 0.95;
                transition: transform 0.3s ease, opacity 0.3s ease;
            }}
            .sidebar-bookworm img:hover {{
                transform: scale(1.05);
                opacity: 1;
            }}

            /* ===== Sidebar Navigation Buttons ===== */
            .stSidebar .stButton > button {{
                background-color: {KPI_BROWN} !important;
                color: white !important;
                border-radius: 8px;
                padding: 12px 16px;
                font-weight: bold;
                font-size: 1em;
                margin-bottom: 10px;
                width: 100%;
                border: none;
                transition: all 0.2s ease-in-out;
            }}
            .stSidebar .stButton > button:hover {{
                background-color: #5e4633 !important;
                box-shadow: 0 0 10px {KPI_BROWN};
            }}
            .stSidebar .stButton > button[data-active="true"] {{
                background-color: {KPI_BROWN_DARK} !important;
                color: white !important;
                border: 2px solid white !important;
            }}

            /* ===== KPI Boxes ===== */
            .green-metric {{
                background: linear-gradient(135deg, {KPI_BROWN}, {KPI_BROWN_DARK});
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
                align-items: center;
                color: white !important;
            }}
            .green-metric h3 {{
                margin-bottom: 8px;
                font-size: 1.3em !important;
                font-weight: bold !important;
                color: white !important;
                text-align: center;
            }}
            .green-metric p {{
                margin: 0;
                font-size: 1.6em !important;
                font-weight: bold !important;
                color: white !important;
                text-align: center;
            }}
            .green-metric:hover {{
                box-shadow: 0 0 24px {KPI_BROWN},
                            0 12px 28px rgba(75, 58, 38, 0.85),
                            inset 0 0 26px rgba(75, 58, 38, 0.95);
                transform: translateY(-4px) scale(1.02);
            }}

            /* ===== Inputs & Dropdowns ===== */
            .stTextInput > div > div > input,
            .stTextArea > div > textarea,
            .stSelectbox > div > div,
            .stNumberInput > div > input,
            .stPasswordInput > div > input {{
                background-color: white !important;
                color: black !important;
                border: 1px solid {KPI_BROWN} !important;
                border-radius: 6px;
                padding: 6px;
                font-size: 0.9em;
            }}
            .stTextInput > div > div > input:focus,
            .stTextArea > div > textarea:focus,
            .stSelectbox > div > div:focus,
            .stNumberInput > div > input:focus,
            .stPasswordInput > div > input:focus {{
                outline: none !important;
                border: 2px solid {KPI_BROWN} !important;
                box-shadow: 0 0 6px {KPI_BROWN};
            }}
            .stSelectbox [role="combobox"] {{
                overflow: visible !important;
                font-size: 0.85em !important;
            }}
            .stSelectbox div[data-baseweb="popover"] {{
                z-index: 9999 !important;
            }}

            /* ===== Expanders ===== */
            div.streamlit-expanderHeader {{
                background-color: {KPI_BROWN} !important;
                color: white !important;
                font-weight: bold !important;
                border-radius: 6px !important;
            }}
            div.streamlit-expanderHeader:hover {{
                background-color: #5e4633 !important;
            }}
            div.streamlit-expanderHeader[aria-expanded="true"] {{
                background-color: {KPI_BROWN_DARK} !important;
                color: white !important;
            }}
            .streamlit-expanderContent {{
                background-color: {PARCHMENT} !important;
                border-left: 3px solid {KPI_BROWN};
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
                max-height: 350px;
                object-fit: contain;
                border-radius: 8px;
                border: 14px solid transparent;
                border-image: linear-gradient(135deg, #e6ddc5, {KPI_BROWN}, {KPI_BROWN_DARK}) 1;
                box-shadow:
                    0 0 12px rgba(75, 58, 38, 0.6),
                    0 6px 16px rgba(0, 0, 0, 0.7),
                    inset 0 0 18px rgba(75, 58, 38, 0.6),
                    inset 2px 2px 8px rgba(0,0,0,0.5);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }}
            .book-cover:hover img {{
                transform: translateY(-6px) scale(1.05);
                box-shadow:
                    0 0 24px rgba(75, 58, 38, 1),
                    0 12px 28px rgba(75, 58, 38, 0.85),
                    inset 0 0 26px rgba(75, 58, 38, 0.95);
                cursor: pointer;
            }}

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

            /* ===== Mobile Optimization ===== */
            @media (max-width: 768px) {{
                .main-title {{
                    font-size: 1.6em;
                }}
                .main-subtitle {{
                    font-size: 1em;
                }}
                .green-metric {{
                    height: auto;
                    padding: 12px;
                }}
                .green-metric h3 {{
                    font-size: 1.1em !important;
                }}
                .green-metric p {{
                    font-size: 1.3em !important;
                }}
                .book-cover img {{
                    max-height: 250px;
                }}
                .stSidebar .stButton > button {{
                    font-size: 0.9em;
                    padding: 10px 12px;
                }}
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )

# =====================
# Sidebar Doors Navigation (auto-close)
# =====================
def show_sidebar_doors(pages):
    st.sidebar.title("Hallway")

    if "page" not in st.session_state:
        st.session_state["page"] = pages[0]

    for page in pages:
        is_active = st.session_state["page"] == page
        if st.sidebar.button(page, use_container_width=True, key=page):
            st.session_state["page"] = page
            # Auto-close sidebar after click
            st.markdown(
                """
                <script>
                let sidebar = window.parent.document.querySelector('section[data-testid="stSidebar"]');
                if (sidebar) {{
                    sidebar.style.display = "none";
                    setTimeout(() => {{
                        sidebar.style.display = "block";
                    }}, 400);
                }}
                </script>
                """,
                unsafe_allow_html=True,
            )

        if is_active:
            st.markdown(
                f"""
                <script>
                var btns = window.parent.document.querySelectorAll('.stSidebar .stButton button');
                btns.forEach(b => {{
                    if(b.innerText.trim() === "{page}") {{
                        b.setAttribute("data-active","true");
                    }} else {{
                        b.removeAttribute("data-active");
                    }}
                }});
                </script>
                """,
                unsafe_allow_html=True,
            )

    # Sidebar Bookworm Image
    st.sidebar.markdown(
        """
        <div class="sidebar-bookworm">
            <img src="bookworm.png" alt="Bookworm"/>
        </div>
        """,
        unsafe_allow_html=True,
    )

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

# =====================
# Dashboard Title
# =====================
def show_dashboard_title():
    st.markdown("<div class='main-title'>Alejandro’s Library</div>", unsafe_allow_html=True)
    st.markdown("<div class='main-subtitle'>A dashboard tracking books, ratings, and genres dynamically</div>", unsafe_allow_html=True)
