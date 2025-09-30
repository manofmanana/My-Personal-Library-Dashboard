import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# 🎨 Apple-inspired playful colors
APPLE_PALETTE = ["#1f77b4", "#d62728", "#ffbf00", "#2ca02c"]  # blue, red, yellow, green


def _wrap_chart(fig, title: str):
    """Wrap chart in a full iMac-style frame (bezel, chin, neck, foot) that expands on mobile for readability."""
    fig_html = fig.to_html(include_plotlyjs="cdn", full_html=False, config={"responsive": True})

    html = f"""
    <style>
        .imac-wrapper {{
            display: flex;
            justify-content: center;
            margin: 40px auto;
            width: 100%;
        }}

        .imac-frame {{
            display: flex; 
            flex-direction: column; 
            align-items: center; 
            width: 90%;
            max-width: 1100px;
        }}

        /* 📱 On mobile, let frame expand wider & taller */
        @media (max-width: 768px) {{
            .imac-frame {{
                width: 100%;
                max-width: 100%;
            }}
            .imac-frame .chart-container {{
                height: 480px !important;
                overflow-x: auto; /* allow scroll for wide charts */
            }}
        }}

        @media (max-width: 480px) {{
            .imac-frame {{
                width: 100%;
                max-width: 100%;
            }}
            .imac-frame .chart-container {{
                height: 520px !important;
                overflow-x: auto;
            }}
        }}
    </style>

    <div class="imac-wrapper">
      <div class="imac-frame">

        <!-- Top bezel -->
        <div style="background: linear-gradient(to bottom, #fdfdfd, #a6a6a6); 
                    height: 16px; width: 100%;
                    border-radius: 14px 14px 0 0;"></div>

        <!-- Chart container -->
        <div class="chart-container" style="background: black; width: 100%;
                    min-height: 400px;
                    border-left: 6px solid transparent; 
                    border-right: 6px solid transparent;
                    border-image: linear-gradient(to bottom, #fdfdfd, #a6a6a6) 1;
                    padding: 20px;  
                    box-sizing: border-box;
                    box-shadow: inset 0 0 20px rgba(255,255,255,0.12),
                                inset 0 0 40px rgba(0,0,0,0.7);">
            {fig_html}
        </div>

        <!-- Chin with glowing Apple circle -->
        <div style="background: linear-gradient(to top, #ededed, #b3b3b3); 
                    height: 70px; width: 100%;
                    border-radius: 0 0 18px 18px; position: relative;">
            <div style="width: 25px; height: 25px; 
                        background: radial-gradient(circle at 30% 30%, #555, black); 
                        border-radius: 50%;
                        position: absolute; top: 50%; left: 50%; 
                        transform: translate(-50%, -50%);
                        box-shadow: 0 0 8px rgba(255,255,255,0.6);">
            </div>
        </div>

        <!-- Trapezoid stand neck -->
        <div style="width: 160px; height: 50px;
                    background: linear-gradient(to bottom, #fdfdfd, #a6a6a6); 
                    clip-path: polygon(20% 0%, 80% 0%, 100% 100%, 0% 100%);
                    border-radius: 0 0 10px 10px; 
                    margin-top: -2px;"></div>

        <!-- Foot stand -->
        <div style="width: 220px; height: 45px; 
                    background: linear-gradient(to bottom, #fefefe, #c0c0c0, #8c8c8c); 
                    border-radius: 8px; 
                    margin-top: -2px;
                    box-shadow: inset 0 2px 6px rgba(255,255,255,0.8),
                                inset 0 -2px 6px rgba(0,0,0,0.2),
                                0 3px 10px rgba(0,0,0,0.4);">
        </div>

      </div>
    </div>
    """
    return html


def _apply_layout(fig, title: str):
    """Apply consistent dark background and axis styling (desktop good, mobile given breathing room)."""
    fig.update_layout(
        title=title,
        paper_bgcolor="black",
        plot_bgcolor="black",
        font=dict(color="white", size=15),
        legend=dict(font=dict(color="white", size=12)),
        margin=dict(l=100, r=60, t=130, b=80),  # 🔼 more top margin so toolbar doesn't overlap
    )
    fig.update_xaxes(
        color="white", gridcolor="#444", 
        title_font=dict(size=13), tickfont=dict(size=11),
        automargin=True,
        title_standoff=40
    )
    fig.update_yaxes(
        color="white", gridcolor="#444",
        title_font=dict(size=13), tickfont=dict(size=11),
        automargin=True,
        title_standoff=50
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

    frame_height = 860  # taller frame

    # Books per Year (Bar Chart)
    by_year = dfx.dropna(subset=["year"]).groupby("year").size().reset_index(name="Books")
    by_year = by_year[by_year["year"] == by_year["year"].astype(int)]
    if not by_year.empty:
        if st.session_state.get("is_mobile", False):
            by_year = by_year.tail(10)
        fig1 = px.bar(by_year, x="year", y="Books", color="Books", color_continuous_scale=APPLE_PALETTE)
        _apply_layout(fig1, "Books per Year")
        st.components.v1.html(_wrap_chart(fig1, "Books per Year"), height=frame_height, scrolling=False)

    # Books per Genre (Sunburst)
    # Mobile tweaks: fewer slices, larger font via uniformtext, outside labels for readability.
    by_genre = dfx.groupby("genre").size().reset_index(name="Books").sort_values("Books", ascending=False)
    if not by_genre.empty:
        if st.session_state.get("is_mobile", False):
            by_genre = by_genre.head(10)  # limit clutter on small screens
        fig2 = px.sunburst(
            by_genre,
            path=["genre"],
            values="Books",
            color="Books",
            color_continuous_scale=APPLE_PALETTE
        )
        fig2.update_traces(
            insidetextorientation="radial",
            textinfo="label+percent entry",
            hovertemplate="<b>%{label}</b><br>Books: %{value}<extra></extra>"
        )
        fig2.update_layout(uniformtext_minsize=12, uniformtext_mode="hide")
        _apply_layout(fig2, "Books per Genre (Sunburst)")
        st.components.v1.html(_wrap_chart(fig2, "Books per Genre (Sunburst)"), height=frame_height, scrolling=False)

    # Average Rating by Genre (Bar Chart w/ labels)
    rated = dfx.dropna(subset=["rating"])
    by_genre_rating = rated.groupby("genre")["rating"].mean().reset_index().sort_values("rating", ascending=False)
    if not by_genre_rating.empty:
        if st.session_state.get("is_mobile", False):
            by_genre_rating = by_genre_rating.head(8)
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
        st.components.v1.html(_wrap_chart(fig3, "Average Rating by Genre"), height=frame_height, scrolling=False)

    # Top 5 Authors (Lollipop Chart: stems + circle markers)
    by_author = dfx.groupby("author").size().reset_index(name="Books").sort_values("Books", ascending=False).head(5)
    if not by_author.empty:
        # Build a lollipop: line from x=0 to x=Books for each author, and a circle at the end
        fig4 = go.Figure()

        authors_order = list(by_author["author"])[::-1]  # reverse for nicer top-down layout
        by_author_sorted = by_author.set_index("author").loc[authors_order].reset_index()

        # stems (lines)
        for _, r in by_author_sorted.iterrows():
            fig4.add_trace(
                go.Scatter(
                    x=[0, r["Books"]],
                    y=[r["author"], r["author"]],
                    mode="lines",
                    line=dict(color=APPLE_PALETTE[0], width=4),
                    showlegend=False
                )
            )
        # lollipop heads (markers + label)
        fig4.add_trace(
            go.Scatter(
                x=by_author_sorted["Books"],
                y=by_author_sorted["author"],
                mode="markers+text",
                marker=dict(size=18, color=APPLE_PALETTE[1], line=dict(color="white", width=2)),
                text=by_author_sorted["Books"],
                textposition="middle right",
                textfont=dict(size=14, color="white"),
                showlegend=False
            )
        )

        fig4.update_yaxes(categoryorder="array", categoryarray=authors_order)
        fig4.update_xaxes(range=[0, max(by_author_sorted["Books"]) * 1.2])  # little breathing room
        _apply_layout(fig4, "Top 5 Authors by Book Count (Lollipop)")
        st.components.v1.html(_wrap_chart(fig4, "Top 5 Authors by Book Count (Lollipop)"), height=frame_height, scrolling=False)

    # Ratings Distribution (Desktop: Violin, Mobile: Histogram)
    if not rated.empty:
        is_mobile = st.session_state.get("is_mobile", False)
        if is_mobile:
            fig5 = px.histogram(rated, x="rating", nbins=20,
                                color_discrete_sequence=APPLE_PALETTE, opacity=0.9)
            fig5.update_xaxes(range=[0, 5])
            _apply_layout(fig5, "Ratings Distribution (Histogram)")
            st.components.v1.html(_wrap_chart(fig5, "Ratings Distribution (Histogram)"), height=frame_height, scrolling=False)
        else:
            rated_for_violin = rated.copy()
            fig5 = px.violin(
                rated_for_violin,
                x="genre",
                y="rating",
                box=True,
                points=False,
                color="genre",
                color_discrete_sequence=APPLE_PALETTE
            )
            fig5.update_yaxes(range=[0, 5])
            _apply_layout(fig5, "Ratings Distribution (Violin)")
            st.components.v1.html(_wrap_chart(fig5, "Ratings Distribution (Violin)"), height=frame_height, scrolling=False)

    # Average Rating by Year (Line Chart)
    by_year_rating = rated.dropna(subset=["year"]).groupby("year")["rating"].mean().reset_index().sort_values("year")
    by_year_rating = by_year_rating[by_year_rating["year"] == by_year_rating["year"].astype(int)]
    if not by_year_rating.empty:
        if st.session_state.get("is_mobile", False):
            by_year_rating = by_year_rating.tail(10)
        fig6 = px.line(by_year_rating, x="year", y="rating", markers=True)
        fig6.update_traces(line=dict(color="#1f77b4"), marker=dict(color="#d62728", size=10))
        fig6.update_yaxes(range=[0, 5])
        _apply_layout(fig6, "Average Rating by Year")
        st.components.v1.html(_wrap_chart(fig6, "Average Rating by Year"), height=frame_height, scrolling=False)
