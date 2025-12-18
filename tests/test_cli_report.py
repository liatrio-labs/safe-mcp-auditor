from pathlib import Path

import pytest
from typer.testing import CliRunner

from safe_mcp_auditor.cli import app


runner = CliRunner()
FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"


def test_cli_root_help() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "report" in result.output


def test_cli_report_group_help() -> None:
    result = runner.invoke(app, ["report", "--help"])
    assert result.exit_code == 0
    assert "validate" in result.output
    assert "normalize" in result.output
    assert "render" in result.output


def test_validate_exit_codes() -> None:
    ok = runner.invoke(
        app, ["report", "validate", "--input", str(FIXTURES_DIR / "report.json")]
    )
    assert ok.exit_code == 0

    needs_review = runner.invoke(
        app,
        [
            "report",
            "validate",
            "--input",
            str(FIXTURES_DIR / "report-missing-ids.json"),
        ],
    )
    assert needs_review.exit_code == 1

    fail = runner.invoke(
        app, ["report", "validate", "--input", str(FIXTURES_DIR / "report-fail.json")]
    )
    assert fail.exit_code == 2


def test_normalize_writes_output_and_exit_codes(tmp_path: Path) -> None:
    out_ok = tmp_path / "normalized.json"
    ok = runner.invoke(
        app,
        [
            "report",
            "normalize",
            "--input",
            str(FIXTURES_DIR / "report.json"),
            "--output",
            str(out_ok),
        ],
    )
    assert ok.exit_code == 0
    assert out_ok.exists()
    assert out_ok.read_text(encoding="utf-8").startswith("{")

    out_needs_review = tmp_path / "with-ids.json"
    needs_review = runner.invoke(
        app,
        [
            "report",
            "normalize",
            "--input",
            str(FIXTURES_DIR / "report-missing-ids.json"),
            "--output",
            str(out_needs_review),
        ],
    )
    assert needs_review.exit_code == 1
    assert out_needs_review.exists()


def test_render_writes_reports_and_refuses_overwrite(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(
        app,
        [
            "report",
            "render",
            "--input",
            str(FIXTURES_DIR / "report.json"),
        ],
    )
    assert result.exit_code == 0

    reports_dir = tmp_path / "reports"
    assert (reports_dir / "example-target-deadbeef-safe-mcp-audit.json").exists()
    assert (reports_dir / "example-target-deadbeef-safe-mcp-audit.md").exists()

    second = runner.invoke(
        app,
        [
            "report",
            "render",
            "--input",
            str(FIXTURES_DIR / "report.json"),
        ],
    )
    assert second.exit_code != 0
    assert "Refusing to overwrite" in second.output


def test_invalid_json_prints_error_and_exits_nonzero(tmp_path: Path) -> None:
    bad = tmp_path / "invalid.json"
    bad.write_text("{", encoding="utf-8")

    result = runner.invoke(app, ["report", "validate", "--input", str(bad)])
    assert result.exit_code != 0
    assert "Invalid JSON" in result.output
