import os
import pytest
from click.testing import CliRunner
from weigh.cli_weigh import cli

def test_cli_log_and_totals(temp_db):
    runner = CliRunner()

    # log a donation
    r = runner.invoke(cli, ["log", "Safeway", "Produce", "8.2"], standalone_mode=False)
    assert r.exit_code == 0
    assert "Logged 8.20 lb from 'Safeway' as 'Produce'" in r.output

    # verify totals
    r = runner.invoke(cli, ["totals"], standalone_mode=False)
    assert r.exit_code == 0
    assert "8.20" in r.output


def test_cli_source_add_and_list(temp_db):
    runner = CliRunner()

    r = runner.invoke(cli, ["source", "add", "Trader Joe's"], standalone_mode=False)
    assert r.exit_code == 0

    r = runner.invoke(cli, ["source", "list"], standalone_mode=False)
    assert "Trader Joe's" in r.output


def test_cli_tail(temp_db):
    runner = CliRunner()

    runner.invoke(cli, ["log", "Safeway", "Produce", "3.0"], standalone_mode=False)
    runner.invoke(cli, ["log", "Safeway", "Dry", "4.0"], standalone_mode=False)

    r = runner.invoke(cli, ["tail", "-n", "2"], standalone_mode=False)
    assert r.exit_code == 0
    assert "3.0" in r.output
    assert "4.0" in r.output


def test_cli_undo(temp_db):
    runner = CliRunner()

    runner.invoke(cli, ["log", "Safeway", "Produce", "5.0"], standalone_mode=False)
    r = runner.invoke(cli, ["undo"], standalone_mode=False)

    assert "Removed entry" in r.output

    r = runner.invoke(cli, ["totals"], standalone_mode=False)
    assert "0.00" in r.output  # nothing left
