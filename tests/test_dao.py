from weigh import dao

def test_dao_add_and_get_sources(temp_db):
    dao.add_source("Whole Foods")
    dao.add_source("Safeway")

    sources = dao.get_sources()
    names = [s["name"] for s in sources]
    assert "Whole Foods" in names
    assert "Safeway" in names
