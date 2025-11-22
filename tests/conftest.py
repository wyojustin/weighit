import pytest
import tempfile
import os
import shutil

from weigh import db as weigh_db

@pytest.fixture
def temp_db(monkeypatch):
    tmpdir = tempfile.mkdtemp()
    db_path = os.path.join(tmpdir, "weigh.db")
    schema_path = os.path.join(os.path.dirname(__file__), "..", "src", "weigh", "schema.sql")

    # reset paths and connection
    weigh_db.init_for_test(db_path, schema_path)

    return {"db_path": db_path, "tmpdir": tmpdir}
