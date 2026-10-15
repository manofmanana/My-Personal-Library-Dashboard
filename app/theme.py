"""Look and feel: fonts, the few custom HTML pieces Streamlit doesn't provide, and chart styling.

Colors and base fonts live in .streamlit/config.toml; this file only adds what the theme can't.
"""
import html

import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

from app.library import stars

INK = "#2b1d14"
MUTED = "#7a6552"
LEATHER = "#9a5b2e"
PALETTE = ["#9a5b2e", "#d4a24c", "#5f7a4f", "#3d5a73", "#b4655f", "#7d6b91", "#c98b5e", "#8aa37b"]
NO_COVER = "app/static/no-cover.svg"

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,700&family=Inter:wght@400;500;600&display=swap');

.block-container { padding-top: 4.5rem; max-width: 1200px; }
@media (max-width: 760px) { .block-container { padding-top: 3.5rem; } }

/* ---- Hero banner ---- */
.hero {
  position: relative; overflow: hidden; border-radius: 22px; min-height: 280px;
  display: flex; align-items: flex-end; padding: clamp(20px, 4vw, 44px);
  background-size: cover; background-position: center;
  box-shadow: 0 18px 40px rgba(43, 29, 20, .25);
}
.hero::before {
  content: ""; position: absolute; inset: 0;
  background: linear-gradient(180deg, rgba(20,12,7,.05) 0%, rgba(20,12,7,.55) 55%, rgba(20,12,7,.85) 100%);
}
.hero > div { position: relative; color: #fff; }
.hero .eyebrow { text-transform: uppercase; letter-spacing: .16em; font-size: .78rem; font-weight: 600; color: #f0c98a; }
.hero h1 { font-family: 'Fraunces', Georgia, serif; color: #fff; font-size: clamp(2rem, 6vw, 3.6rem); line-height: 1.05; margin: .2em 0 .25em; padding: 0; }
.hero p { margin: 0; max-width: 36rem; font-size: clamp(.95rem, 2vw, 1.12rem); color: rgba(255,255,255,.88); }

/* ---- Quote ---- */
.quote { margin: 26px 0 8px; padding: 18px 22px; border-left: 4px solid #d4a24c; background: #fbf7ef;
         border-radius: 0 14px 14px 0; font-family: 'Fraunces', Georgia, serif; font-size: 1.15rem; color: #3b2a20; }
.quote cite { display: block; margin-top: 6px; font-family: 'Inter', sans-serif; font-style: normal; font-size: .85rem; color: #7a6552; }

/* ---- Stat cards ---- */
.stats { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; margin: 18px 0 8px; }
@media (max-width: 760px) { .stats { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; } }
.stat { background: #fff; border: 1px solid #ecdfca; border-radius: 18px; padding: 16px 18px; box-shadow: 0 6px 18px rgba(43,29,20,.06); }
.stat .label { font-size: .78rem; text-transform: uppercase; letter-spacing: .08em; color: #7a6552; font-weight: 600; }
.stat .value { font-family: 'Fraunces', Georgia, serif; font-size: clamp(1.4rem, 4vw, 2rem); color: #2b1d14; line-height: 1.15; margin-top: 4px;
               white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.stat .hint { font-size: .8rem; color: #9a8673; margin-top: 2px; }

/* ---- Book covers ---- */
.shelf { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 22px 18px; margin-top: 8px; }
@media (max-width: 760px) { .shelf { grid-template-columns: repeat(auto-fill, minmax(104px, 1fr)); gap: 16px 12px; } }
.shelf.row { display: flex; overflow-x: auto; scroll-snap-type: x mandatory; padding-bottom: 10px; }
.shelf.row .book { flex: 0 0 140px; scroll-snap-align: start; }
@media (max-width: 760px) { .shelf.row .book { flex-basis: 112px; } }
.book { text-decoration: none !important; color: inherit !important; display: block; }
.book .cover { position: relative; aspect-ratio: 2 / 3; border-radius: 6px 12px 12px 6px; overflow: hidden;
               background: #e2d4bd url('app/static/no-cover.svg') center / cover;
               box-shadow: 0 2px 4px rgba(43,29,20,.15), 0 10px 22px rgba(43,29,20,.18);
               transition: transform .25s ease, box-shadow .25s ease; }
.book .cover::after { content: ""; position: absolute; inset: 0 auto 0 0; width: 7px;
                      background: linear-gradient(90deg, rgba(0,0,0,.25), rgba(255,255,255,.12), transparent); }
.book .cover img { width: 100%; height: 100%; object-fit: cover; display: block; }
.book:hover .cover { transform: translateY(-5px) rotate(-.6deg); box-shadow: 0 4px 8px rgba(43,29,20,.18), 0 18px 32px rgba(43,29,20,.25); }
.book .title { font-weight: 600; font-size: .92rem; line-height: 1.25; margin-top: 10px; color: #2b1d14;
               display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.book .author { font-size: .8rem; color: #7a6552; margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.book .meta { display: flex; justify-content: space-between; align-items: center; gap: 6px; margin-top: 5px; font-size: .76rem; }
.book .stars { color: #c4892b; letter-spacing: .5px; white-space: nowrap; }
.book .chip { background: #efe4d2; color: #6b5340; border-radius: 99px; padding: 1px 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 55%; }
@media (max-width: 760px) { .book .title { font-size: .82rem; } .book .meta .chip { display: none; } }

.section-note { color: #7a6552; margin-top: -.6rem; }
</style>
"""


def inject():
    st.html(CSS)


def hero(eyebrow: str, title: str, subtitle: str, image: str = "app/static/banner.jpg"):
    st.html(f"""
    <div class="hero" style="background-image: url('{image}')">
      <div><div class="eyebrow">{html.escape(eyebrow)}</div><h1>{html.escape(title)}</h1><p>{html.escape(subtitle)}</p></div>
    </div>""")


def quote(text: str, author: str):
    st.html(f'<blockquote class="quote">“{html.escape(text)}”<cite>— {html.escape(author)}</cite></blockquote>')


def stat_cards(cards):
    """cards: [(label, value, hint)]"""
    items = "".join(
        f'<div class="stat"><div class="label">{html.escape(label)}</div>'
        f'<div class="value">{html.escape(str(value))}</div><div class="hint">{html.escape(hint)}</div></div>'
        for label, value, hint in cards
    )
    st.html(f'<div class="stats">{items}</div>')


def book_shelf(df, link_for, row: bool = False):
    """Covers in a responsive grid (or one swipeable row), with title, author, rating, and genre."""
    cards = []
    for book in df.itertuples():
        cover = html.escape(book.cover_url or NO_COVER, quote=True)
        title = html.escape(book.title or "Untitled")
        author = html.escape(book.author or "Unknown author")
        genre = html.escape(book.genre or "")
        link = html.escape(link_for(book.title, book.author, book.isbn), quote=True)
        cards.append(
            f'<a class="book" href="{link}" target="_blank" rel="noopener" title="{title} by {author}">'
            f'<div class="cover"><img src="{cover}" alt="Cover of {title}" loading="lazy"></div>'
            f'<div class="title">{title}</div><div class="author">{author}</div>'
            f'<div class="meta"><span class="stars">{stars(book.rating)}</span><span class="chip">{genre}</span></div></a>'
        )
    st.html(f'<div class="shelf{" row" if row else ""}">{"".join(cards)}</div>')


def _register_chart_template():
    template = go.layout.Template()
    template.layout = go.Layout(
        font=dict(family="Inter, sans-serif", color=INK, size=13),
        title=dict(font=dict(family="Fraunces, Georgia, serif", size=18, color=INK), x=0, xanchor="left"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        colorway=PALETTE,
        margin=dict(l=10, r=10, t=50, b=10),
        xaxis=dict(gridcolor="#eadfcd", zeroline=False, linecolor="#d8c7ad"),
        yaxis=dict(gridcolor="#eadfcd", zeroline=False, linecolor="#d8c7ad"),
        hoverlabel=dict(bgcolor="#2b1d14", font=dict(color="#fff", family="Inter, sans-serif")),
        bargap=0.25,
    )
    pio.templates["library"] = template


_register_chart_template()


def chart(fig, height: int = 340):
    fig.update_layout(template="library", height=height)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
