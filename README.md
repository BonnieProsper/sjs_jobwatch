# SJS JobWatch

**Monitor and track changes in the SJS New Zealand job board with automated email alerts.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🎯 What Does This Do?

SJS JobWatch automatically:
- **Scrapes** job listings from the SJS New Zealand public service job board
- **Tracks** changes over time (new jobs, removed jobs, modified postings)
- **Sends** email alerts when relevant changes occur
- **Filters** by region, category, and change severity
- **Stores** historical snapshots for analysis

**Perfect for job seekers** who want to stay on top of new opportunities without manually checking the site every day.

---

## ✨ Features

### Core Functionality
- ✅ **Automated Scraping**: Fetch job listings from SJS with configurable filters
- ✅ **Change Detection**: Identify new, removed, and modified job postings
- ✅ **Email Alerts**: Beautiful HTML emails with change summaries
- ✅ **Flexible Filters**: Region, category, keyword search support
- ✅ **Historical Tracking**: Keep snapshots of past job boards
- ✅ **CLI Interface**: Easy-to-use command-line tools

### Technical Highlights
- 🏗️ **Clean Architecture**: Separation of concerns (scraping → storage → diffing → alerts)
- 🔒 **Type Safe**: Full type hints with Pydantic models
- 📊 **Rich Output**: Beautiful terminal tables with the `rich` library
- 🧪 **Testable**: Pure functions, dependency injection, no global state
- 📝 **Well Documented**: Comprehensive docstrings and examples

---

## 📦 Installation

### Requirements
- Python 3.10 or higher
- Gmail account (for sending email alerts)

### Quick Install

```bash
# Clone the repository
git clone https://github.com/yourusername/sjs-jobwatch.git
cd sjs-jobwatch

# Install with pip
pip install -e .

# Or install with optional dev dependencies
pip install -e ".[dev]"
```

### Verify Installation

```bash
sjs-jobwatch --help
```

---

## 🚀 Quick Start

### 1. Scrape Your First Snapshot

```bash
# Scrape all jobs
sjs-jobwatch scrape

# Or filter by region
sjs-jobwatch scrape --region Auckland

# Or filter by category
sjs-jobwatch scrape --category ICT

# Search with keyword
sjs-jobwatch scrape --keyword "data analyst"
```

### 2. View Job Changes

After running a second scrape, view the differences:

```bash
# Compare latest snapshot with previous one
sjs-jobwatch diff

# Compare with snapshot from 2 scrapes ago
sjs-jobwatch diff --since 2

# View as plain text instead of table
sjs-jobwatch diff --format text
```

### 3. Set Up Email Alerts

```bash
# Add your email subscription
sjs-jobwatch alerts add your.email@example.com \
    --region Auckland \
    --category ICT \
    --frequency daily \
    --hour 9

# Test the alert (dry run)
sjs-jobwatch alerts test your.email@example.com --dry-run

# View all subscriptions
sjs-jobwatch alerts list
```

### 4. Run the Alert Service

```bash
# Run once and exit
sjs-jobwatch run --once

# Run continuously (checks hourly)
sjs-jobwatch run

# Dry run (no emails sent)
sjs-jobwatch run --dry-run
```

---

## 🔧 Configuration

### Email Setup (Required for Alerts)

SJS JobWatch uses Gmail SMTP to send emails. You'll need to create an **App Password**:

1. Go to [Google Account Settings](https://myaccount.google.com/)
2. Security → 2-Step Verification → App passwords
3. Generate a new app password
4. Set environment variables:

```bash
export GMAIL_ADDRESS="your.email@gmail.com"
export GMAIL_APP_PASSWORD="xxxx xxxx xxxx xxxx"
```

**On Windows:**
```powershell
$env:GMAIL_ADDRESS="your.email@gmail.com"
$env:GMAIL_APP_PASSWORD="xxxx xxxx xxxx xxxx"
```

**Persistent Setup (Linux/Mac):**
```bash
# Add to ~/.bashrc or ~/.zshrc
echo 'export GMAIL_ADDRESS="your.email@gmail.com"' >> ~/.bashrc
echo 'export GMAIL_APP_PASSWORD="xxxx xxxx xxxx xxxx"' >> ~/.bashrc
source ~/.bashrc
```

### Advanced Configuration

Edit `src/sjs_jobwatch/core/config.py` to customize:
- Request delays and timeouts
- Snapshot retention policies
- Email formatting
- Logging levels

---

## 📚 CLI Reference

### Scraping

```bash
# Basic scrape
sjs-jobwatch scrape

# With filters
sjs-jobwatch scrape --region Wellington --category "Policy"

# With keyword search
sjs-jobwatch scrape --keyword "senior developer"
```

**Available Regions:**
`All`, `Auckland`, `Wellington`, `Canterbury`, `Bay of Plenty`, `Waikato`, `Otago`, `Hawke's Bay`, `Manawatu-Wanganui`, `Northland`, `Taranaki`, `Nelson`, `Marlborough`, `Southland`, `Gisborne`, `Tasman`, `West Coast`, `Overseas`

**Available Categories:**
`All`, `ICT`, `Allied Health`, `Corporate`, `Education`, `Engineering`, `Facilities`, `Finance & Accounting`, `Health`, `Human Resources`, `Legal`, `Management`, `Operations`, `Planning`, `Policy`, `Science`, `Social Services`, `Trades & Services`, `Other`

### Viewing Changes

```bash
# Show differences from latest snapshot
sjs-jobwatch diff

# Compare with older snapshots
sjs-jobwatch diff --since 3

# Plain text output
sjs-jobwatch diff --format text
```

### Managing Snapshots

```bash
# List recent snapshots
sjs-jobwatch list

# List more snapshots
sjs-jobwatch list --limit 50

# Export latest snapshot
sjs-jobwatch export csv jobs.csv
sjs-jobwatch export json jobs.json

# Export older snapshot
sjs-jobwatch export csv jobs-old.csv --snapshot 5
```

### Managing Alert Subscriptions

```bash
# Add subscription
sjs-jobwatch alerts add email@example.com \
    --region Auckland \
    --category ICT \
    --frequency daily \
    --hour 9 \
    --severity medium

# List subscriptions
sjs-jobwatch alerts list

# Remove subscription
sjs-jobwatch alerts remove email@example.com

# Test alert
sjs-jobwatch alerts test email@example.com
sjs-jobwatch alerts test email@example.com --dry-run
```

**Alert Options:**
- `--frequency`: `daily` or `weekly`
- `--hour`: 0-23 (UTC time)
- `--severity`: `low`, `medium`, `high`, `critical`
- `--region`: Filter alerts to specific region
- `--category`: Filter alerts to specific category

### Running the Service

```bash
# Run once and exit
sjs-jobwatch run --once

# Run continuously
sjs-jobwatch run

# Dry run (no emails)
sjs-jobwatch run --dry-run --once

# Verbose logging
sjs-jobwatch run --once -v
```

---

## 📊 How It Works

### Architecture

```
┌──────────────┐
│   Scraper    │  Fetch jobs from SJS website
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Snapshot   │  Save point-in-time snapshot
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Diff Engine │  Compare snapshots
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Filters &   │  Apply subscription filters
│  Severity    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│Email Renderer│  Generate HTML/text emails
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ SMTP Sender  │  Deliver emails
└──────────────┘
```

### Data Flow

1. **Scraping**: HTTP request → BeautifulSoup → Extract `__NEXT_DATA__` script → Parse JSON
2. **Storage**: Snapshot → JSON file with timestamp filename
3. **Diffing**: Load two snapshots → Compare by job ID → Identify changes
4. **Filtering**: Apply region/category/severity filters per subscription
5. **Rendering**: Changes → Jinja2 templates → HTML + text emails
6. **Delivery**: SMTP → Gmail → Recipient

### Why Not Use Playwright?

The original project used Playwright (headless browser), but the SJS site is server-side rendered with Next.js, which embeds all job data in `<script id="__NEXT_DATA__">` tags. This means we can use simple HTTP requests + BeautifulSoup, which is:
- ✅ **Faster** (no browser overhead)
- ✅ **Lighter** (no Chromium dependencies)
- ✅ **Simpler** (fewer moving parts)
- ✅ **More reliable** (fewer things to break)

---

## 🗂️ Project Structure

```
sjs-jobwatch/
├── src/
│   └── sjs_jobwatch/
│       ├── core/              # Domain models and business logic
│       │   ├── models.py      # Pydantic models (Job, Snapshot, etc.)
│       │   ├── config.py      # Configuration management
│       │   └── diff.py        # Diff engine
│       ├── ingestion/         # Web scraping
│       │   └── scraper.py     # SJS scraper implementation
│       ├── storage/           # Persistence
│       │   └── snapshots.py   # Snapshot storage
│       ├── alerts/            # Email notifications
│       │   ├── email.py       # Email rendering and sending
│       │   ├── subscriptions.py  # Subscription management
│       │   └── templates/     # Email templates
│       │       ├── alert_email.html
│       │       └── alert_email.txt
│       └── cli/               # Command-line interface
│           └── main.py        # CLI entry point
├── data/                      # Data directory (created automatically)
│   ├── snapshots/            # Historical snapshots
│   ├── exports/              # Exported data
│   └── jobwatch.log          # Application logs
├── tests/                     # Test suite
├── docs/                      # Additional documentation
├── pyproject.toml            # Project metadata and dependencies
├── README.md                 # This file
└── .gitignore
```

---

## 🧪 Development

### Running Tests

```bash
pytest
pytest -v                    # Verbose
pytest --cov=sjs_jobwatch   # With coverage
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint
ruff check src/ tests/

# Type check
mypy src/
```

### Adding Features

The codebase is designed to be extensible:

1. **New scrapers**: Subclass or extend `SJSScraper`
2. **New filters**: Add methods to `AlertSubscription`
3. **New output formats**: Add commands to CLI
4. **New notification channels**: Implement new sinks (e.g., Slack, Discord)

---

## 🐛 Troubleshooting

### "Could not find __NEXT_DATA__ script tag"

The SJS website structure may have changed. Check the HTML source of the jobs page and update the scraper accordingly.

### "Failed to send email"

1. Verify `GMAIL_ADDRESS` and `GMAIL_APP_PASSWORD` are set
2. Check that you're using an **App Password**, not your regular password
3. Ensure Gmail SMTP is not blocked by your firewall
4. Try the test command: `sjs-jobwatch alerts test your@email.com --dry-run`

### "No snapshots found"

Run `sjs-jobwatch scrape` at least once to create initial data.

### Slow scraping

The scraper includes a 2-second delay between requests to be respectful to the server. This is intentional and configurable in `config.py`.

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests
5. Run quality checks (`black`, `ruff`, `mypy`, `pytest`)
6. Commit (`git commit -m 'Add amazing feature'`)
7. Push (`git push origin feature/amazing-feature`)
8. Open a Pull Request

---

## License

MIT License - see LICENSE file for details.

---

## 🔮 Roadmap

Future enhancements planned:
- [ ] Web dashboard for viewing trends
- [ ] Database backend (SQLite/PostgreSQL)
- [ ] Machine learning for job recommendations
- [ ] Multi-site support (beyond SJS)
- [ ] Slack/Discord integrations
- [ ] Job similarity detection
- [ ] Salary trend analysis
- [ ] API for integrations

---

**Happy job hunting! 🎯**
