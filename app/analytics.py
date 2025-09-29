import streamlit as st
import plotly.express as px
import pandas as pd

# 🎨 Apple-inspired playful colors
APPLE_PALETTE = ["#1f77b4", "#d62728", "#ffbf00", "#2ca02c"]  # blue, red, yellow, green

def _wrap_chart(fig, title: str):
    """Wrap chart in an iMac-style frame that is responsive for desktop & mobile."""
    html = f"""
    <style>
        @media (max-width: 768px) {{
            .imac-frame {{
                width: 100% !important;
                margin: 20px auto !important;
            }}
            .imac-frame .chart-container {{
                padding: 10px !important;
            }}
        }}
    </style>

    <div class="imac-frame" style="
        display: flex; 
        flex-direction: column; 
        align-items: center; 
        margin: 40px auto; 
        width: 95%;
        max-width: 1100px;
    ">
        <!-- Top bezel -->
        <div style="background: linear-gradient(to bottom, #fdfdfd, #a6a6a6); 
                    height: 14px; width: 100%;
                    border-radius: 14px 14px 0 0;"></div>

        <!-- Chart container -->
        <div class="chart-container" style="background: black; width: 100%;
                    border-left: 6px solid transparent; 
                    border-right: 6px solid transparent;
                    border-image: linear-gradient(to bottom, #fdfdfd, #a6a6a6) 1;
                    padding: 20px;  
                    box-sizing: border-box;
                    box-shadow: inset 0 0 20px rgba(255,255,255,0.12),
                                inset 0 0 40px rgba(0,0,0,0.7);">
            {fig.to_html(include_plotlyjs="cdn", full_html=False)}
        </div>

        <!-- Chin -->
        <div style="background: linear-gradient(to top, #ededed, #b3b3b3); 
                    height: 60px; width: 100%;
                    border-radius: 0 0 18px 18px; position: relative;">
            <div style="width: 32px; height: 32px; 
                        background: radial-gradient(circle at 30% 30%, #555, black); 
                        border-radius: 50%;
                        position: absolute; top: 50%; left: 50%; 
                        transform: translate(-50%, -50%);
                        box-shadow: 0 0 6px rgba(255,255,255,0.6);">
            </div>
        </div>

        <!-- Neck -->
        <div style="width: 120px; height: 40px;
                    background: linear-gradient(to bottom, #fdfdfd, #a6a6a6); 
                    clip-path: polygon(20% 0%, 80% 0%, 100% 100%, 0% 100%);
                    border-radius: 0 0 8px 8px; 
                    margin-top: -2px;"></div>

        <!-- Foot stand -->
        <div style="width: 180px; height: 35px; 
                    background: linear-gradient(to bottom, #fefefe, #c0c0c0, #8c8c8c); 
                    border-radius: 8px; 
                    margin-top: -2px;
                    box-shadow: inset 0 2px 6px rgba(255,255,255,0.8),
                                inset 0 -2px 6px rgba(0,0,0,0.2),
                                0 3px 10px rgba(0,0,0,0.4);">
        </div>
    </div>
    """
    return html


def _apply_layout(fig, title: str):
    """Apply consistent dark background and axis styling with responsive margins."""
    fig.update_layout(
        title=title,
        paper_bgcolor="black",
        plot_bgcolor="black",
        font=dict(color="white", size=14),
        legend=dict(font=dict(color="white", size=11)),
        margin=dict(l=60, r=40, t=60, b=80),  # reduced margins for better fit
    )
    fig.update_xaxes(
        color="white", gridcolor="#444", 
        title_font=dict(size=13), tickfont=dict(size=11),
        title_standoff=25
    )
    fig.update_yaxes(
        color="white", gridcolor="#444",
        title_font=dict(size=13), tickfont=dict(size=11),
        title_standoff=40
    )


def show_charts(df: pd.DataFrame):
    if df.empty:
        st.info("No data for charts yet!")
        return

    dfx = df.copy()
    dfx["year"] = pd.to_numeric(dfx["year"], errors="coerce").astype("Int64")
    dfx["rating"] = pd.to_numeric(dfx["rating"], errors="coerce")
    dfx["genre"] = dfx["genre"].fillna("Unknown")
    dfx["author"] = dfx["author"].fillna("Unknown")

    st.subheader("Computer Lab Dashboard")

    # Books per Year
    by_year = dfx.dropna(subset=["year"]).groupby("year").size().reset_index(name="Books")
    by_year = by_year[by_year["year"] == by_year["year"].astype(int)]
    if not by_year.empty:
        fig1 = px.bar(by_year, x="year", y="Books", color="Books", color_continuous_scale=APPLE_PALETTE)
        _apply_layout(fig1, "Books per Year")
        st.components.v1.html(_wrap_chart(fig1, "Books per Year"), height=600, scrolling=False)

    # Books per Genre
    by_genre = dfx.groupby("genre").size().reset_index(name="Books").sort_values("Books", ascending=True)
    if not by_genre.empty:
        fig2 = px.bar(by_genre, x="Books", y="genre", orientation="h", color="Books",
                      color_continuous_scale=APPLE_PALETTE)
        _apply_layout(fig2, "Books per Genre")
        st.components.v1.html(_wrap_chart(fig2, "Books per Genre"), height=600, scrolling=False)

    # Average Rating by Genre
    rated = dfx.dropna(subset=["rating"])
    by_genre_rating = rated.groupby("genre")["rating"].mean().reset_index().sort_values("rating", ascending=False)
    if not by_genre_rating.empty:
        fig3 = px.bar(by_genre_rating, x="genre", y="rating", color="rating",
                      color_continuous_scale=APPLE_PALETTE, text="rating")
        fig3.update_traces(
            texttemplate="%{text:.2f}",
            textposition="outside",
            textfont=dict(size=12),
            cliponaxis=False
        )
        fig3.update_yaxes(range=[0, 5.5])
        _apply_layout(fig3, "Average Rating by Genre")
        st.components.v1.html(_wrap_chart(fig3, "Average Rating by Genre"), height=600, scrolling=False)

    # Top 5 Authors
    by_author = dfx.groupby("author").size().reset_index(name="Books").sort_values("Books", ascending=False).head(5)
    if not by_author.empty:
        fig4 = px.bar(by_author, x="author", y="Books", color="Books",
                      color_continuous_scale=APPLE_PALETTE, text="Books")
        _apply_layout(fig4, "Top 5 Authors by Book Count")
        st.components.v1.html(_wrap_chart(fig4, "Top 5 Authors by Book Count"), height=600, scrolling=False)

    # Ratings Distribution
    if not rated.empty:
        fig5 = px.histogram(rated, x="rating", nbins=20, color_discrete_sequence=APPLE_PALETTE, opacity=0.9)
        fig5.update_xaxes(range=[0, 5])
        _apply_layout(fig5, "Ratings Distribution")
        st.components.v1.html(_wrap_chart(fig5, "Ratings Distribution"), height=600, scrolling=False)

    # Average Rating by Year
    by_year_rating = rated.dropna(subset=["year"]).groupby("year")["rating"].mean().reset_index().sort_values("year")
    by_year_rating = by_year_rating[by_year_rating["year"] == by_year_rating["year"].astype(int)]
    if not by_year_rating.empty:
        fig6 = px.line(by_year_rating, x="year", y="rating", markers=True)
        fig6.update_traces(line=dict(color="#1f77b4"), marker=dict(color="#d62728", size=8))
        fig6.update_yaxes(range=[0, 5])
        _apply_layout(fig6, "Average Rating by Year")
        st.components.v1.html(_wrap_chart(fig6, "Average Rating by Year"), height=600, scrolling=False)
