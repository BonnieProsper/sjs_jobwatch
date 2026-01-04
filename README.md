folder structure

src/
  sjs_sitewatch/
    __init__.py

    cli.py                  # Entry point (argparse / typer)
    config.py               # Categories, regions, thresholds

    ingestion/
      browser.py            # Fetch HTML
      extract.py            # Parse raw listings
      normalize.py          # Normalize into Job models

    domain/
      job.py                # Job model (dataclass)
      snapshot.py           # Snapshot = list[Job] + metadata
      diff.py               # Pure diff logic
      explain.py            # Field-level explanations
      trends.py             # Rolling growth, counts

    storage/
      filesystem.py         # Save/load snapshots (JSON)

    alerts/
      email.py              # Email formatting + sending
      filters.py            # Severity/category filtering

    reporting/
      console.py            # Rich tables
      export.py             # CSV/JSON export

tests/
  test_diff.py
  test_explain.py
  test_trends.py
  test_alerts.py
pyproject.toml
readme.md
testing.md



## Email Alerts

SJS SiteWatch can automatically notify users of meaningful job market changes via email, including configurable filters by role type, region, and change severity. Alerts are designed for scheduled execution in production environments.


## Architecture Overview

SJS SiteWatch is intentionally designed as a layered system:

### Domain Layer
- Job, Snapshot, DiffResult
- Deterministic diffing
- Explainable change severity

### Alerts Layer
- Pure filtering & dispatch logic
- No I/O in decision code
- Email formatting isolated

### Scheduling Layer
- APScheduler cron-based jobs
- Stateless job execution
- Subscriptions persisted to JSON

### CLI Layer
- Inspection (diffs, summaries)
- Alert management
- Dry-run support

This separation allows:
- Easy testing
- Safe refactors
- Future web/API extensions





- test everything out, test emails/manual lookup etc, clean up repo, commit to git 

