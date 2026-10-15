"""Alejandro's Library: a Streamlit dashboard over a small SQLite database of books I've read.

Run with:  streamlit run main.py
"""
import streamlit as st
from dotenv import load_dotenv

from app import db_utils, theme, views

load_dotenv()  # lets a local .env file provide ADMIN_PASSWORD

st.set_page_config(page_title="Alejandro's Library", page_icon="static/favicon.png", layout="wide")


@st.cache_resource
def prepare_database_once():
    db_utils.prepare_database()


prepare_database_once()
theme.inject()
st.logo("static/bookworm.png", size="large")

pages = {
    "home": st.Page(views.home, title="Library", icon=":material/local_library:", default=True),
    "shelf": st.Page(views.shelf, title="Bookstacks", icon=":material/menu_book:", url_path="bookstacks"),
    "stats": st.Page(views.stats, title="Computer Lab", icon=":material/insights:", url_path="computer-lab"),
    "manage": st.Page(views.manage, title="Stack Maintenance", icon=":material/edit_note:", url_path="maintenance"),
}
st.session_state["pages"] = pages  # so pages can link to each other

page = st.navigation(list(pages.values()), position="top")
views.show_flash()
page.run()
