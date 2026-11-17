markdown
# Operational Runbook

This runbook provides support procedures, log locations, and recovery steps for operational teams maintaining this solution.

---

## 1. Monitoring & Log Locations

* **Log File Location:** Configured via `LOG_FILE_PATH` in `.env` (default: `./logs/application.log`).
* **Log Rotation:** Logs automatically rotate at **5 MB** and retain up to **5 backup files** (`application.log.1` through `application.log.5`).
* **Log Format:** `ISO-8601 Timestamp | LEVEL | module:function | Message`

### Severity Levels
* **`INFO`:** Normal workflow milestones (startup, record counts, output file creation).
* **`WARNING`:** Non-fatal anomalies (skipped optional records, retry attempts).
* **`ERROR`:** Recoverable or expected operational failures (missing input file, validation error) that halted execution safely.
* **`CRITICAL`:** Unexpected system failures requiring immediate engineering review.

---

## 2. Common Failure Scenarios & Resolution

### Issue 1: Immediate Exit with `Configuration error` on `stderr`
* **Symptom:** Process exits immediately with code `1` before creating a log file.
* **Cause:** One or more required environment variables (`API_KEY`, `DATABASE_URL`) are missing, empty, or improperly formatted in `.env`.
* **Resolution:**
  1. Compare `.env` against `.env.example`.
  2. Verify all required secrets are populated with non-empty values.
  3. Re-run the workflow.

### Issue 2: `Missing required file or directory` (`FileNotFoundError`)
* **Symptom:** Log records `ERROR | package_name.main:main | Missing required file or directory`.
* **Cause:** The configured `DATA_INPUT_DIR` or expected source file does not exist at runtime.
* **Resolution:**
  1. Verify that upstream data delivery completed successfully.
  2. Confirm `DATA_INPUT_DIR` in `.env` points to the exact mounted or local directory path.
  3. Confirm the service account running the script has read permissions on the directory.

### Issue 3: Process Fails Mid-Run — Is Output Safe to Use?
* **Behavior:** Output files are written to a temporary file first and atomically moved to `DATA_OUTPUT_DIR` **only** after all processing steps succeed.
* **Resolution:** If a run fails, no partial or corrupted report will overwrite prior completed outputs. Resolve the underlying error logged in `application.log` and re-run safely.

---

## 3. Escalation Checklist

When escalating an unresolved failure to the development team, attach:
1. The relevant section of `application.log` (including full stack traces).
2. The exact timestamp and `APP_ENV` (`development`, `staging`, or `production`) of the failed run.
3. Sample sanitized input headers (with sensitive customer data removed).
