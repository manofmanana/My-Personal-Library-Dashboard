import os
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


@pytest.fixture
def db_path(tmp_path, monkeypatch):
    """A throwaway copy of the real library, so tests never change books_normalized.db."""
    path = tmp_path / "books.db"
    shutil.copy(ROOT / "books_normalized.db", path)
    monkeypatch.setenv("LIBRARY_DB", str(path))
    from app import db_utils
    monkeypatch.setattr(db_utils, "DB_PATH", str(path))
    return str(path)


@pytest.fixture
def empty_db(tmp_path):
    """A brand-new database built from schema.sql."""
    import sqlite3
    path = tmp_path / "empty.db"
    with sqlite3.connect(path) as conn:
        conn.executescript((ROOT / "schema.sql").read_text())
    return str(path)
