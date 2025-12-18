from pathlib import Path

import typer


app = typer.Typer(no_args_is_help=True, add_completion=False)


@app.command()
def validate(
    input: Path = typer.Option(..., "--input", exists=True, readable=True),
) -> None:
    """Validate an audit report JSON file against the schema."""
    raise typer.Exit(code=0)


@app.command()
def normalize(
    input: Path = typer.Option(..., "--input", exists=True, readable=True),
    output: Path = typer.Option(..., "--output"),
) -> None:
    """Normalize an audit report (stable IDs + ordering) and write JSON."""
    raise typer.Exit(code=0)


@app.command()
def render(
    input: Path = typer.Option(..., "--input", exists=True, readable=True),
) -> None:
    """Render a deterministic Markdown report under reports/."""
    raise typer.Exit(code=0)
