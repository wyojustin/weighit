from click.testing import CliRunner
from weigh.cli_weigh import cli

def test_end_to_end(temp_db):
    runner = CliRunner()

    runner.invoke(cli, ["source", "add", "Wegmans"], standalone_mode=False)
    runner.invoke(cli, ["log", "Wegmans", "Dairy", "7.5"], standalone_mode=False)

    r = runner.invoke(cli, ["totals"], standalone_mode=False)
    assert "7.50" in r.output
