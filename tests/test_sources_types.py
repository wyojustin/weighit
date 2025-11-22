# test_sources_types.py
from weigh import logger_core


def test_sources_loaded(temp_db):
    sources = logger_core.get_sources_dict()
    assert "Trader Joe's" in sources
    assert "Wegmans" in sources
    assert len(sources) >= 7


def test_types_loaded(temp_db):
    types = logger_core.get_types_dict()
    assert "Produce" in types
    assert "Dry" in types
    assert len(types) >= 7
