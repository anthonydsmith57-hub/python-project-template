"""Unit tests for CSV ingestion, schema validation, and department aggregation."""

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from package_name.ingestion import TransactionRecord, load_and_validate_transactions
from package_name.processing import format_summary_as_csv, summarize_by_department


def test_load_and_validate_transactions_succeeds(tmp_path: Path) -> None:
    """Valid CSV rows should parse into typed TransactionRecord instances."""
    csv_file = tmp_path / "transactions.csv"
    csv_file.write_text(
        "transaction_id,transaction_date,department,amount\n"
        "TX-100,2026-11-15,Engineering,1250.50\n"
        "TX-101,2026-11-16,sales,499.99\n",
        encoding="utf-8",
    )

    records = load_and_validate_transactions(csv_file)

    assert len(records) == 2
    assert records[0].amount == Decimal("1250.50")
    assert records[1].transaction_date == date(2026, 11, 16)


def test_load_rejects_missing_headers(tmp_path: Path) -> None:
    """CSV missing required columns should raise ValueError immediately."""
    csv_file = tmp_path / "bad_headers.csv"
    csv_file.write_text(
        "transaction_id,department\nTX-100,Engineering\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Missing required CSV headers"):
        load_and_validate_transactions(csv_file)


def test_load_rejects_negative_amount(tmp_path: Path) -> None:
    """Negative or zero transaction amounts should fail validation."""
    csv_file = tmp_path / "negative_amount.csv"
    csv_file.write_text(
        "transaction_id,transaction_date,department,amount\n"
        "TX-100,2026-11-15,Engineering,-50.00\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Data validation failed at row 2"):
        load_and_validate_transactions(csv_file)


def test_summarize_by_department_aggregates_accurately() -> None:
    """Pure aggregation function should group, normalize, and sum exact Decimals."""
    records = [
        TransactionRecord(
            transaction_id="1",
            transaction_date=date(2026, 11, 15),
            department="sales",
            amount=Decimal("100.10"),
        ),
        TransactionRecord(
            transaction_id="2",
            transaction_date=date(2026, 11, 16),
            department=" SALES ",
            amount=Decimal("200.25"),
        ),
    ]

    summaries = summarize_by_department(records)
    csv_text = format_summary_as_csv(summaries)

    assert len(summaries) == 1
    assert summaries[0].department == "SALES"
    assert summaries[0].transaction_count == 2
    assert summaries[0].total_amount == Decimal("300.35")
    assert "SALES,2,300.35" in csv_text
