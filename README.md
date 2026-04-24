# AI-Powered Business Reports Generator

A Python automation tool that turns CSV business data into a structured HTML
performance report. It can run fully offline for local dry-runs, or optionally
use OpenRouter or a locally cached Hugging Face model for AI-generated insights.

The app supports:

- CSV data validation
- KPI calculation
- Deterministic local report insights
- Optional AI insight generation
- HTML report preview
- SMTP email delivery
- Scheduled report runs

## Quick Start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python run_report.py --dry-run
```

The dry-run command writes `output/report.html` and does not send email.

## Configuration

Edit `.env` for local settings. The app reads these values through `config.py`.

Required only for real email sending:

```env
EMAIL_SENDER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_RECIPIENTS=recipient1@example.com,recipient2@example.com
```

Useful defaults:

```env
DATA_SOURCE_PATH=data/sample_data.csv
REPORT_FREQUENCY=daily
REPORT_TIME=09:00
AI_ENABLED=false
```

AI is disabled by default so the app runs cleanly without network access. When
`AI_ENABLED=false`, reports use deterministic local insight text.

To use OpenRouter:

```env
AI_ENABLED=true
OPENROUTER_API_KEY=your-openrouter-key
OPENROUTER_MODEL=deepseek/deepseek-r1-0528:free
```

To use a locally cached Hugging Face model:

```powershell
pip install -r requirements-ai.txt
```

Then set:

```env
AI_ENABLED=true
USE_LOCAL_MODEL=true
HF_MODEL=distilgpt2
```

The local model loader uses cached files only. It will not download models during
a report run.

## Commands

```powershell
python run_report.py --dry-run
python run_report.py --dry-run --output report.html
python run_report.py
python run_report.py --schedule
python test_api_connection.py
python -m pytest tests/ -v
```

Windows launchers are also included:

- `PREVIEW_REPORT.bat`
- `QUICK_START.bat`
- `RUN_REPORT.bat`
- `RUN_TESTS.bat`

## CSV Data

The CSV must include a `Date` column.

Example:

```csv
Date,Revenue,Sales,Customer_Count
2026-01-15,10000,150,500
2026-01-16,10500,155,510
```

Supported metric columns include:

- `Revenue`
- `Sales`
- `Customer_Count`
- `Orders`
- `Returns`
- `Customer_Satisfaction`

Invalid dates or non-numeric values in numeric metric columns will stop the run
with a validation error.

## OpenRouter Diagnostics

If OpenRouter calls fail, run:

```powershell
python test_api_connection.py
```

The diagnostic checks:

- General internet access
- DNS resolution for `openrouter.ai`
- OpenRouter endpoint reachability
- Whether `OPENROUTER_API_KEY` is loaded

It never prints the API key value.

## Project Structure

```text
Email_report_app/
|-- run_report.py
|-- config.py
|-- business_metrics.py
|-- ai_insights.py
|-- automated_email.py
|-- test_api_connection.py
|-- requirements.txt
|-- requirements-ai.txt
|-- .env.example
|-- data/
|   `-- sample_data.csv
|-- output/
|-- tests/
`-- utils/
```

## Use Case

This project demonstrates how automated reporting can reduce repetitive manual
work, generate faster business insights, and provide a practical foundation for
SaaS-style reporting workflows.

## Future Improvements

- Add a UI dashboard for report visualization
- Integrate multiple data sources such as APIs, CSV files, and databases
- Add richer report templates
- Deploy as a web-based reporting tool

## Notes

- `.env` is ignored by git and should contain secrets only on your local machine.
- `output/` and `logs/` are generated folders and are ignored by git.
- Dry-run mode validates data, calculates KPIs, generates report HTML, and skips SMTP.
- Live email mode validates email credentials and recipients before sending.

## Author

Ihsan Hadhrami

- Portfolio: https://ihsanhadhrami.github.io/My-Portfolio/
- GitHub: https://github.com/ihsanhadhrami
