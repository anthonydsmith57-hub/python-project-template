markdown
# Project Name

Brief one-sentence description of what this solution does, what inputs it consumes, and what outputs it generates.

---

## Architecture & Data Flow

```text
[Source Inputs / APIs]
         │
         ▼
  1. Ingestion (ingestion.py)      ──► Validates file existence & raw schemas
         │
         ▼
  2. Processing (processing.py)    ──► Pure transformations & business rules
         │
         ▼
  3. Reporting (reporting.py)      ──► Atomic output generation (summary_report.csv)
         │
         ▼
[Output Directory & Rotating Logs]
```

### Project Structure

```text
project_root/
├── .github/workflows/ci.yml   # Automated CI quality and security checks
├── docs/runbook.md            # Operational troubleshooting and support guide
├── src/package_name/
│   ├── config.py              # Pydantic environment & secret validation
│   ├── logger.py              # Centralized console & rotating file logging
│   └── main.py                # Entry point & workflow orchestration
├── tests/                     # Automated pytest unit and failure tests
├── .env.example               # Template for required environment variables
├── .pre-commit-config.yaml    # Local Git pre-commit hooks
└── pyproject.toml             # Dependencies, Ruff, mypy, and pytest rules
```

---

## Prerequisites

* **Python:** 3.11 or higher
* **Environment Variables:** Credentials and paths configured via `.env` (see `.env.example`)
* **Required Directories:** Input directory must exist before execution (`DATA_INPUT_DIR`)

---

## Installation & Setup

1. **Clone the repository and create a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate        # Windows PowerShell: .venv\Scripts\Activate.ps1
   ```

2. **Install the package and development tools:**
   ```bash
   pip install -e ".[dev]"
   ```

3. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```
   Open `.env` and populate actual credentials and directory paths. **Never commit `.env` to version control.**

4. **Enable pre-commit hooks (for developers):**
   ```bash
   pre-commit install
   ```

---

## Running the Application

Ensure your input files are placed in `DATA_INPUT_DIR`, then execute:

```bash
python -m package_name.main
```

* **Exit Code `0`:** Workflow completed successfully; output written to `DATA_OUTPUT_DIR`.
* **Exit Code `1`:** Workflow failed; inspect console output or `LOG_FILE_PATH` for details.

---

## Quality, Testing & Security Checks

Run the full suite of automated checks before submitting a pull request:

```bash
ruff check .               # Linting, import sorting, and Bandit security rules
ruff format --check .      # Formatting verification
mypy src                   # Strict static type checking
pytest                     # Unit tests with coverage report
pip-audit                  # Dependency vulnerability scan
```
