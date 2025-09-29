import streamlit as st
import pandas as pd
from app import db_utils

GOLD = "#d4af37"

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
    st.subheader("Library")

    if not df.empty:
        df_covers = df
        if df_covers.empty:
            st.warning("No books match this filter.")
        else:
            cols = st.columns(5, gap="small")
            for i, (_, row) in enumerate(df_covers.iterrows()):
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
