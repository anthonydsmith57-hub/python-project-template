"""Application entry point and high-level workflow orchestration."""

import logging
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile

from pydantic import ValidationError

from package_name.config import AppConfig, load_configuration
from package_name.ingestion import load_and_validate_transactions  # <-- ADDED
from package_name.logger import setup_logging
from package_name.processing import (  # <-- ADDED
    format_summary_as_csv,
    summarize_by_department,
)

logger = logging.getLogger(__name__)

SOURCE_FILE_NAME = "transactions.csv"  # <-- ADDED
OUTPUT_FILE_NAME = "summary_report.csv"  # <-- ADDED


def validate_environment(config: AppConfig) -> None:
    """Verify that required input and output directories are ready.

    Args:
        config: Validated application configuration.

    Raises:
        FileNotFoundError: If the required input directory does not exist.
    """
    if not config.data_input_dir.exists() or not config.data_input_dir.is_dir():
        raise FileNotFoundError(
            f"Required input directory does not exist: {config.data_input_dir}"
        )

    config.data_output_dir.mkdir(parents=True, exist_ok=True)


def write_output_atomically(content: str, destination: Path) -> None:
    """Write output to a temporary file first and atomically move to destination.

    Prevents partial or corrupted output files if an error occurs mid-write.

    Args:
        content: Text content to write to the output file.
        destination: Final target path for the completed output file.
    """
    with NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=destination.parent,
        delete=False,
    ) as temp_file:
        temp_path = Path(temp_file.name)
        try:
            temp_file.write(content)
        except Exception:
            temp_path.unlink(missing_ok=True)
            raise

    temp_path.replace(destination)


def run_workflow(config: AppConfig) -> Path:
    """Execute the core application steps in sequence.

    Args:
        config: Validated application configuration.

    Returns:
        Path to the completed output file.
    """
    validate_environment(config)

    source_file = config.data_input_dir / SOURCE_FILE_NAME
    records = load_and_validate_transactions(source_file)

    summaries = summarize_by_department(records)
    csv_output = format_summary_as_csv(summaries)

    output_file = config.data_output_dir / OUTPUT_FILE_NAME
    write_output_atomically(csv_output, output_file)

    logger.info("Generated summary across %d departments.", len(summaries))
    return output_file


def main() -> int:
    """Run the application with structured error handling and clean exit codes.

    Returns:
        0 if the workflow succeeded, 1 if an error occurred.
    """
    try:
        config = load_configuration()
    except ValidationError as exc:
        # Logging is not configured yet; write configuration failure to stderr
        sys.stderr.write(f"Configuration error: {exc}\n")
        return 1

    setup_logging(log_level=config.log_level, log_file_path=config.log_file_path)
    logger.info("Starting workflow in '%s' environment.", config.app_env)

    try:
        output_path = run_workflow(config)
    except FileNotFoundError as exc:
        logger.error("Missing required file or directory: %s", exc)
        return 1
    except ValueError as exc:
        logger.error("Input data validation error: %s", exc)
        return 1
    except Exception:
        logger.exception("Workflow failed due to an unexpected error.")
        return 1

    logger.info("Workflow completed successfully. Output saved to: %s", output_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
