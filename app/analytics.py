import streamlit as st
import plotly.express as px
import pandas as pd

# Dark theme background + brighter copper/gold palette
DARK_BROWN = "#2c1b0c"
COPPER_PALETTE = ["#FFD700", "#FFB347", "#FF8C42"]

def _apply_dark_layout(fig, title: str):
    fig.update_layout(
        title=title,
        paper_bgcolor=DARK_BROWN,
        plot_bgcolor=DARK_BROWN,
        font=dict(color="white"),
        legend=dict(font=dict(color="white"))
    )
    fig.update_xaxes(color="white", gridcolor="#444")
    fig.update_yaxes(color="white", gridcolor="#444")

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
    if not by_year.empty:
        fig1 = px.bar(by_year, x="year", y="Books", color="Books",
                      color_continuous_scale=COPPER_PALETTE)
        _apply_dark_layout(fig1, "Books per Year")
        st.plotly_chart(fig1, use_container_width=True)

    # Books per Genre
    by_genre = dfx.groupby("genre").size().reset_index(name="Books").sort_values("Books", ascending=True)
    if not by_genre.empty:
        fig2 = px.bar(by_genre, x="Books", y="genre", orientation="h", color="Books",
                      color_continuous_scale=COPPER_PALETTE)
        _apply_dark_layout(fig2, "Books per Genre")
        st.plotly_chart(fig2, use_container_width=True)

    # Average Rating by Genre
    rated = dfx.dropna(subset=["rating"])
    by_genre_rating = rated.groupby("genre")["rating"].mean().reset_index().sort_values("rating", ascending=False)
    if not by_genre_rating.empty:
        fig3 = px.bar(by_genre_rating, x="genre", y="rating", color="rating",
                      color_continuous_scale=COPPER_PALETTE, text="rating")
        fig3.update_traces(texttemplate="%{text:.2f}")
        fig3.update_yaxes(range=[0, 5])
        _apply_dark_layout(fig3, "Average Rating by Genre")
        st.plotly_chart(fig3, use_container_width=True)

    # Top 5 Authors
    by_author = dfx.groupby("author").size().reset_index(name="Books").sort_values("Books", ascending=False).head(5)
    if not by_author.empty:
        fig4 = px.bar(by_author, x="author", y="Books", color="Books",
                      color_continuous_scale=COPPER_PALETTE, text="Books")
        _apply_dark_layout(fig4, "Top 5 Authors by Book Count")
        st.plotly_chart(fig4, use_container_width=True)

    # Ratings Distribution
    if not rated.empty:
        fig5 = px.histogram(rated, x="rating", nbins=20,
                            color_discrete_sequence=COPPER_PALETTE, opacity=0.9)
        fig5.update_xaxes(range=[0, 5])
        _apply_dark_layout(fig5, "Ratings Distribution")
        st.plotly_chart(fig5, use_container_width=True)

    # Average Rating by Year
    by_year_rating = rated.dropna(subset=["year"]).groupby("year")["rating"].mean().reset_index().sort_values("year")
    if not by_year_rating.empty:
        fig6 = px.line(by_year_rating, x="year", y="rating", markers=True)
        fig6.update_traces(line=dict(color="#FFB347"), marker=dict(color="#FFD700", size=8))
        fig6.update_yaxes(range=[0, 5])
        _apply_dark_layout(fig6, "Average Rating by Year")
        st.plotly_chart(fig6, use_container_width=True)
