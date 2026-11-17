"""Pure business logic for aggregating and summarizing validated transactions."""

from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal

from package_name.ingestion import TransactionRecord


@dataclass(frozen=True)
class DepartmentSummary:
    """Immutable summary metrics for a single department."""

    department: str
    transaction_count: int
    total_amount: Decimal


def summarize_by_department(
    records: list[TransactionRecord],
) -> list[DepartmentSummary]:
    """Aggregate transaction counts and total amounts grouped by department.

    Args:
        records: List of validated TransactionRecord items.

    Returns:
        A deterministically sorted list of DepartmentSummary objects.
    """
    totals: dict[str, Decimal] = defaultdict(lambda: Decimal("0.00"))
    counts: dict[str, int] = defaultdict(int)

    for record in records:
        normalized_dept = record.department.strip().upper()
        totals[normalized_dept] += record.amount
        counts[normalized_dept] += 1

    return [
        DepartmentSummary(
            department=dept,
            transaction_count=counts[dept],
            total_amount=totals[dept].quantize(Decimal("0.01")),
        )
        for dept in sorted(totals)
    ]


def format_summary_as_csv(summaries: list[DepartmentSummary]) -> str:
    """Serialize DepartmentSummary records into a CSV-formatted string.

    Args:
        summaries: List of aggregated department summaries.

    Returns:
        CSV content string including header row.
    """
    lines = ["department,transaction_count,total_amount"]
    for item in summaries:
        lines.append(f"{item.department},{item.transaction_count},{item.total_amount}")
    return "\n".join(lines) + "\n"
