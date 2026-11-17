"""Source data ingestion and strict row-level schema validation."""

import csv
import logging
from datetime import date
from decimal import Decimal
from pathlib import Path

from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger(__name__)

REQUIRED_HEADERS: frozenset[str] = frozenset(
    {"transaction_id", "transaction_date", "department", "amount"}
)


class TransactionRecord(BaseModel):
    """Validated representation of a single incoming transaction row."""

    transaction_id: str = Field(..., min_length=1)
    transaction_date: date
    department: str = Field(..., min_length=1)
    amount: Decimal = Field(..., gt=Decimal("0.00"))


def load_and_validate_transactions(file_path: Path) -> list[TransactionRecord]:
    """Read a CSV file and validate headers and rows against TransactionRecord.

    Args:
        file_path: Path to the source CSV file.

    Returns:
        A list of validated TransactionRecord objects.

    Raises:
        FileNotFoundError: If the CSV file does not exist.
        ValueError: If required headers are missing, the file is empty,
            or any row fails validation.
    """
    if not file_path.exists() or not file_path.is_file():
        raise FileNotFoundError(f"Source CSV file not found: {file_path}")

    with file_path.open(mode="r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)

        if reader.fieldnames is None:
            raise ValueError(f"Source CSV file is empty: {file_path}")

        actual_headers = set(reader.fieldnames)
        missing_headers = REQUIRED_HEADERS - actual_headers
        if missing_headers:
            missing_list = ", ".join(sorted(missing_headers))
            raise ValueError(f"Missing required CSV headers: {missing_list}")

        validated_records: list[TransactionRecord] = []
        for row_number, raw_row in enumerate(reader, start=2):
            try:
                record = TransactionRecord.model_validate(raw_row)
                validated_records.append(record)
            except ValidationError as exc:
                logger.error(
                    "Validation failed on row %d of %s: %s",
                    row_number,
                    file_path.name,
                    exc.errors(include_url=False),
                )
                raise ValueError(
                    f"Data validation failed at row {row_number} in {file_path.name}"
                ) from exc

    logger.info(
        "Successfully loaded and validated %d records from %s.",
        len(validated_records),
        file_path.name,
    )
    return validated_records
