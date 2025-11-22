# test_logging.py
from weigh import logger_core


def test_log_entry_and_query(temp_db):
    logger_core.log_entry(10.5, "Trader Joe's", "Produce")
    logger_core.log_entry(5.0, "Safeway", "Dry")

    logs = logger_core.get_last_logs(10)
    assert len(logs) == 2

    assert logs[0]["weight_lb"] in (10.5, 5.0)
    assert logs[1]["weight_lb"] in (10.5, 5.0)


def test_undo_last(temp_db):
    logger_core.log_entry(7.7, "Wegmans", "Meat")

    removed = logger_core.undo_last_entry()
    assert removed is not None

    logs = logger_core.get_last_logs(10)
    assert logs[0]["deleted"] == 1


def test_totals_today(temp_db):
    logger_core.log_entry(3.0, "Whole Foods", "Bread")
    logger_core.log_entry(2.0, "Whole Foods", "Bread")

    total = logger_core.totals_today_weight()
    assert abs(total - 5.0) < 1e-6
