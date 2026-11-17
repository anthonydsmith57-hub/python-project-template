"""Unit tests for configuration loading and main workflow execution."""

from pathlib import Path

import pytest

from package_name.main import main


def test_main_fails_when_secrets_missing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Ensure main() exits with code 1 when required secrets are absent."""
    monkeypatch.chdir(tmp_path)  # Prevent reading a local .env file
    monkeypatch.delenv("API_KEY", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)

    exit_code = main()

    assert exit_code == 1


def test_main_fails_when_input_dir_missing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Ensure main() exits with code 1 and creates no output if input dir is missing."""
    missing_input = tmp_path / "does_not_exist"
    output_dir = tmp_path / "output"
    log_file = tmp_path / "logs" / "test.log"

    monkeypatch.setenv("API_KEY", "test_secret_key")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///test.db")
    monkeypatch.setenv("DATA_INPUT_DIR", str(missing_input))
    monkeypatch.setenv("DATA_OUTPUT_DIR", str(output_dir))
    monkeypatch.setenv("LOG_FILE_PATH", str(log_file))

    exit_code = main()

    assert exit_code == 1
    assert not (output_dir / "summary_report.csv").exists()


def test_main_fails_when_csv_invalid(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Ensure main() exits with code 1 and creates no output if CSV data is invalid."""
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "transactions.csv").write_text(
        "transaction_id,transaction_date,department,amount\n"
        "TX-100,2026-11-15,Engineering,-50.00\n",
        encoding="utf-8",
    )

    output_dir = tmp_path / "output"
    log_file = tmp_path / "logs" / "test.log"

    monkeypatch.setenv("API_KEY", "test_secret_key")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///test.db")
    monkeypatch.setenv("DATA_INPUT_DIR", str(input_dir))
    monkeypatch.setenv("DATA_OUTPUT_DIR", str(output_dir))
    monkeypatch.setenv("LOG_FILE_PATH", str(log_file))

    exit_code = main()

    assert exit_code == 1
    assert not (output_dir / "summary_report.csv").exists()
    assert "Input data validation error" in log_file.read_text(encoding="utf-8")


def test_main_succeeds_with_valid_environment(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Ensure main() creates the expected output file and returns exit code 0."""
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "transactions.csv").write_text(
        "transaction_id,transaction_date,department,amount\n"
        "TX-100,2026-11-15,Engineering,1250.50\n"
        "TX-101,2026-11-16,Engineering,249.50\n",
        encoding="utf-8",
    )

    output_dir = tmp_path / "output"
    log_file = tmp_path / "logs" / "test.log"

    monkeypatch.setenv("API_KEY", "test_secret_key")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///test.db")
    monkeypatch.setenv("DATA_INPUT_DIR", str(input_dir))
    monkeypatch.setenv("DATA_OUTPUT_DIR", str(output_dir))
    monkeypatch.setenv("LOG_FILE_PATH", str(log_file))

    exit_code = main()
    report_file = output_dir / "summary_report.csv"

    assert exit_code == 0
    assert report_file.exists()
    assert "ENGINEERING,2,1500.00" in report_file.read_text(encoding="utf-8")
    assert log_file.exists()
