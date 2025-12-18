import typer

from safe_mcp_auditor import __version__
from safe_mcp_auditor.report.commands import app as report_app


app = typer.Typer(no_args_is_help=True, add_completion=False)


@app.callback()
def callback(
    version: bool = typer.Option(
        False,
        "--version",
        help="Print version and exit.",
        is_eager=True,
    ),
) -> None:
    if version:
        typer.echo(__version__)
        raise typer.Exit(code=0)


def main() -> None:
    app()


app.add_typer(report_app, name="report")
