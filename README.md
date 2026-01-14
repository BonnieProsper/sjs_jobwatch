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

TREND CONTRACT

A trend is a derived signal computed over ≥2 diffs
A trend never depends on CLI or alert logic
A trend may downgrade or suppress single-diff severity


### Exporting job snapshots

You can export any snapshot to CSV or JSON using:

```python
from sjs_sitewatch.storage.export import export_jobs_csv


## Exporting job snapshots

You can export the most recent job snapshot to CSV or JSON:

```bash
sjs-sitewatch export --format csv --out jobs.csv
sjs-sitewatch export --format json --out jobs.json

## Alert Architecture

Alerts are processed in three stages:

1. **Pipeline**
   - Diffs + trends → scored, filtered changes
2. **Renderer**
   - Pure text/HTML formatting (Jinja templates)
3. **Sinks**
   - Side effects (console output, email delivery, etc.)

This separation allows:
- Deterministic testing
- Multiple delivery mechanisms
- Clear responsibility boundaries

## Exporting Job Data

You can export the current snapshot to CSV or JSON:

```bash
sjs-sitewatch export csv jobs.csv
sjs-sitewatch export json jobs.json

Alerts Architecture
Snapshots → Diff → Trends → Scorer → Pipeline → Sink


Scorer: assigns severity + explanation (pure logic)

Pipeline: applies subscription filtering (pure logic)

Sinks: side-effectful delivery (console, email)

This separation keeps the system testable, extensible, and production-grade.

## Automatic Alerting Service

SJS Sitewatch includes a background scheduler that automatically emails users
when relevant job market changes occur.

### How it works
- Users register alert subscriptions (email, severity, frequency, filters)
- A scheduler evaluates new snapshots daily or weekly
- Alerts are scored, filtered, and emailed automatically

### Running the service
```bash
python -m sjs_sitewatch.runtime.service \
  --data-dir data \
  --subscriptions subscriptions.json

Architecture
Snapshot Store
   ↓
Diff + Trends
   ↓
AlertScorer
   ↓
AlertPipeline
   ↓
DeliveryService
   ↓
Email / Console

Why this design

pure domain logic

sinks are swappable

scheduler is isolated

testable at every layer

Operations

--once

dry-run

background service

            ┌────────────┐
            │ Snapshots  │
            │ (Filesystem)│
            └─────┬──────┘
                  │
           diff + trends
                  │
          ┌───────▼────────┐
          │ AlertPipeline  │
          │  - scoring     │
          │  - filtering   │
          └───────┬────────┘
                  │
          ┌───────▼────────┐
          │ Delivery       │
          │  (Email, CLI)  │
          └────────────────┘


## Why this project exists

Job boards change constantly — listings appear, disappear, and mutate
without any explanation. For job seekers, this creates uncertainty and
manual effort: refreshing pages, re-running searches, and missing
important changes.

**sjs_sitewatch** exists to solve a specific, real problem:

> Detect meaningful changes in job listings over time and notify users
> automatically, reliably, and explainably.

This project was intentionally designed as a **production-style backend
service**, not a demo or script. Its goals are to demonstrate:

- Snapshot-based data modeling (immutable historical records)
- Deterministic diffing and trend analysis
- Subscription-driven alert evaluation
- Pluggable notification sinks (email, filesystem, dry-run)
- Long-running scheduling with safe one-shot execution
- Testability of time, IO, and side effects

The architecture mirrors patterns used in real data and platform
engineering systems:
- append-only storage
- pure domain logic
- side-effect isolation
- explicit scheduling boundaries

This makes the project both **useful** and **representative of real
backend engineering work**.

## Running as a background service

### Linux (systemd)

Create a service file:

```ini
[Unit]
Description=SJS Sitewatch
After=network.target

[Service]
ExecStart=/usr/bin/sjs-sitewatch run
Restart=always
User=sitewatch
WorkingDirectory=/opt/sitewatch

[Install]
WantedBy=multi-user.target

Enable and start

sudo systemctl enable sitewatch
sudo systemctl start sitewatch


- test everything out, test emails/manual lookup etc, clean up repo, commit to git 

# TODO: add region based filtering, parse down entire repo, unneeded code and files etc