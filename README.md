SJS SiteWatch

Track meaningful changes on the SJS New Zealand job board and receive targeted email alerts.

Why this project exists

The SJS job site updates frequently, but it does not provide reliable alerts, history, or change context. Manually checking listings makes it easy to miss relevant updates or waste time rereading unchanged postings.

SJS SiteWatch is a small, deterministic CLI tool that:

snapshots the job board over time

detects and explains meaningful changes

emails only what matches your criteria

It is intentionally narrow in scope and designed to be easy to reason about and operate.

What it does

Fetches job listings from the public SJS website

Stores point-in-time snapshots as JSON

Computes diffs between snapshots (new, removed, modified jobs)

Scores changes by severity

Filters alerts by region, category, and severity

Sends concise email summaries via SMTP

What it does not do

No web UI

No database

No background daemon required

No scraping frameworks or headless browsers

This is a CLI-first tool meant to run on a schedule (cron / Task Scheduler).

Installation

Python 3.10+

git clone https://github.com/yourusername/sjs-sitewatch.git
cd sjs-sitewatch
pip install -e .


Verify:

sjs-sitewatch --help

Quick start

Create an alert subscription:

sjs-sitewatch alerts add you@email.com --ict-only --region "All"


Run once:

sjs-sitewatch run --once


Dry-run (no email sent):

sjs-sitewatch run --once --dry-run

Email setup

Email delivery uses Gmail SMTP with an App Password.

Set environment variables:

macOS / Linux

export GMAIL_ADDRESS="your.email@gmail.com"
export GMAIL_APP_PASSWORD="xxxx xxxx xxxx xxxx"


Windows (PowerShell)

setx GMAIL_ADDRESS "your.email@gmail.com"
setx GMAIL_APP_PASSWORD "xxxx xxxx xxxx xxxx"


Restart your shell after setting these.

Scheduling (recommended)

Run daily using your OS scheduler.

Linux / macOS (cron):

0 9 * * * sjs-sitewatch run


Windows (Task Scheduler):

Program: sjs-sitewatch

Arguments: run

Trigger: Daily

How it works
Snapshot → Diff → Score → Filter → Render → Send


Snapshots are stored as JSON files

Diffs are computed purely by job ID

Alert logic is deterministic and testable

Delivery is handled by pluggable sinks (console, email)

The SJS site embeds job data in __NEXT_DATA__, so the scraper uses standard HTTP requests instead of a headless browser.

Project structure
sjs_sitewatch/
├── domain/        # core models, diffs, trends
├── ingestion/    # scraping
├── alerts/       # scoring, pipelines, sinks
├── users/        # alert subscriptions
├── runtime/      # scheduler / runner
├── cli/          # command-line interface

Development

Run tests:

pytest


Lint:

ruff check src tests

Status

This repository represents a complete, frozen v1.

Future ideas (not implemented here):

additional alert sinks (Slack, Discord)

richer trend reporting

multi-site support

License

MIT
