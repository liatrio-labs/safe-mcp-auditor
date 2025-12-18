from typer.testing import CliRunner

from safe_mcp_auditor.cli import app


runner = CliRunner()


def test_cli_root_help() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "report" in result.stdout


def test_cli_report_group_help() -> None:
    result = runner.invoke(app, ["report", "--help"])
    assert result.exit_code == 0
    assert "validate" in result.stdout
    assert "normalize" in result.stdout
    assert "render" in result.stdout
