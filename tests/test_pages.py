"""Render every page with Streamlit's test runner and make sure nothing crashes."""
from streamlit.testing.v1 import AppTest

PAGE = """
from app import theme, views
theme.inject()
views.{name}()
"""


def run_page(name):
    return AppTest.from_string(PAGE.format(name=name), default_timeout=60).run()


def test_home_page(db_path):
    at = AppTest.from_file("../main.py", default_timeout=60).run()
    assert not at.exception
    assert [s.value for s in at.subheader] == ["Latest reads", "All-time favorites"]


def test_bookstacks_search(db_path):
    at = run_page("shelf")
    assert not at.exception
    at.text_input(key="shelf_query").input("zzzz no such book").run()
    assert not at.exception
    assert any("No books match" in i.value for i in at.info)


def test_computer_lab(db_path):
    at = run_page("stats")
    assert not at.exception
    assert len(at.get("plotly_chart")) >= 4


def test_maintenance_locked_without_password(db_path, monkeypatch):
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)
    at = run_page("manage")
    assert not at.exception
    assert any("Editing is turned off" in i.value for i in at.info)


def test_maintenance_unlocks_with_password(db_path, monkeypatch):
    monkeypatch.setenv("ADMIN_PASSWORD", "open sesame")
    at = run_page("manage")
    at.text_input[0].input("wrong").run()
    at.button[0].click().run()
    assert any("Incorrect" in e.value for e in at.error)
    at.text_input[0].input("open sesame").run()
    at.button[0].click().run()
    assert not at.exception
    assert [t.label for t in at.tabs] == ["Add a book", "Edit a book", "Remove a book"]
