# cli_weigh.py  — Click-based CLI for the weigh system

import click
from weigh import dao
from weigh.logger_core import (
    log_entry,
    undo_last_entry,
    totals_today_weight,
    get_last_logs,
    get_sources_dict,
    get_types_dict,
)


# =====================================================
# ROOT COMMAND
# =====================================================

@click.group()
def cli():
    """Weigh CLI tool — log, manage, and inspect food donations."""
    pass


# =====================================================
# LOGGING COMMANDS
# =====================================================

@cli.command()
@click.argument("source")
@click.argument("type")
@click.argument("weight", type=float)
def log(source, type, weight):
    """
    Log a new weight entry.

    Example:
        weigh log "Trader Joe's" Produce 5.4
    """
    log_entry(weight, source, type)
    click.echo(f"Logged {weight:.2f} lb from '{source}' as '{type}'")


@cli.command()
def undo():
    """Undo the most recent log entry."""
    row = undo_last_entry()
    if row:
        click.echo(f"Removed entry: {row}")
    else:
        click.echo("No entries to undo.")


@cli.command()
def totals():
    """Show today's total logged weight."""
    total = totals_today_weight()
    click.echo(f"Today's total: {total:.2f} lb")


@cli.command()
@click.option("-n", default=10, help="Number of rows to show")
def tail(n):
    """Show the last N log entries."""
    rows = get_last_logs(n)
    for r in rows:
        click.echo(dict(r))


# =====================================================
# SOURCE MANAGEMENT
# =====================================================

@cli.group()
def source():
    """Manage food donation sources."""
    pass


@source.command("list")
def source_list():
    """List all sources."""
    for s in dao.get_sources():
        click.echo(f"{s['id']:2d}  {s['name']}")


@source.command("add")
@click.argument("name")
def source_add(name):
    """Add a new donation source."""
    dao.add_source(name)
    click.echo(f"Added source: {name}")


# =====================================================
# TYPE MANAGEMENT
# =====================================================

@cli.group()
def type():
    """Manage food types."""
    pass


@type.command("list")
def type_list():
    """List all food types."""
    for t in dao.get_types():
        click.echo(f"{t['id']:2d}  {t['name']}")


@type.command("add")
@click.argument("name")
def type_add(name):
    """Add a new food type."""
    dao.add_type(name)
    click.echo(f"Added type: {name}")


# =====================================================
# ENTRY POINT
# =====================================================

def main():
    """Entry point for the installed `weigh` console script."""
    cli(standalone_mode=False)
    
if __name__ == "__main__":
    main()
