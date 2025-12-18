import json
from pathlib import Path

import typer
from pydantic import ValidationError

from safe_mcp_auditor.report.models import Report, Status
from safe_mcp_auditor.report.normalize import normalize_report, serialize_report_json


app = typer.Typer(no_args_is_help=True, add_completion=False)


def _exit_code_for_status(status: Status) -> int:
    return {Status.PASS: 0, Status.NEEDS_REVIEW: 1, Status.FAIL: 2}[status]


def _load_report(input_path: Path) -> Report:
    try:
        data = json.loads(input_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise typer.BadParameter(f"Invalid JSON: {exc}") from exc

    try:
        return Report.model_validate(data)
    except ValidationError as exc:
        raise typer.BadParameter(str(exc)) from exc


@app.command()
def validate(
    input: Path = typer.Option(..., "--input", exists=True, readable=True),
) -> None:
    """Validate an audit report JSON file against the schema."""
    report = _load_report(input)
    typer.echo("Report is valid")
    raise typer.Exit(code=_exit_code_for_status(report.status))


@app.command()
def normalize(
    input: Path = typer.Option(..., "--input", exists=True, readable=True),
    output: Path = typer.Option(..., "--output"),
) -> None:
    """Normalize an audit report (stable ordering) and write JSON."""
    report = _load_report(input)
    normalized = normalize_report(report)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(serialize_report_json(normalized), encoding="utf-8")

    typer.echo(str(output))
    raise typer.Exit(code=_exit_code_for_status(normalized.status))


@app.command()
def render(
    input: Path = typer.Option(..., "--input", exists=True, readable=True),
) -> None:
    """Render a deterministic Markdown report under reports/."""
    raise typer.Exit(code=0)
