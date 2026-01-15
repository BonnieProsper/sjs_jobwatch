import subprocess
import sys


def test_cli_help_runs():
    result = subprocess.run(
        [sys.executable, "-m", "sjs_sitewatch.cli.cli", "--help"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "usage" in result.stdout.lower()


def test_cli_summary_runs_empty(tmp_path, monkeypatch):
    monkeypatch.setenv("SJS_SITEWATCH_DATA_DIR", str(tmp_path))

    result = subprocess.run(
        [sys.executable, "-m", "sjs_sitewatch.cli.main", "--summary"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
