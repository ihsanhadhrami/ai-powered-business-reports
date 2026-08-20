# Automated Email Report (Simple, Impactful)

This project generates an automated business performance email report with
KPIs, interactive charts, and AI-powered insights. It also ships as a
browser-based web app — see [Web App](#web-app) below.

## 🚀 Quick Start (Windows)

### **Option 1: Double-Click to Run (Easiest)**

1. **Install dependencies** (first time only):
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. **Configure your settings** — copy `.env.example` to `.env` and fill in
   your values (see [Configuration](#️-configuration-secure) below).

3. **Run the app** - Choose one:
   - **`QUICK_START.bat`** - Send email immediately
   - **`PREVIEW_REPORT.bat`** - Preview without sending
   - **`RUN_REPORT.bat`** - Interactive menu with options

### **Option 2: Command Line**

```powershell
# Preview report (no email sent)
python run_report.py --dry-run

# Send email now
python run_report.py

# Run on schedule (daily/weekly/monthly)
python run_report.py --schedule
```

---

## 📊 How to Add Your Data

1. Place your CSV file in the **`data/`** folder
2. Point the app at it via `.env`:
   ```env
   DATA_SOURCE_PATH=data/your_data.csv
   ```

### Required CSV Format:
```csv
Date,Revenue,Sales,Customer_Count
2026-01-15,10000,150,500
2026-01-16,10500,155,510
```

**Required columns:**
- `Date` (format: YYYY-MM-DD)

**Optional columns** (use any combination):
- `Revenue`, `Sales`, `Customer_Count`, `Orders`, `Returns`, `Customer_Satisfaction`

Invalid dates or non-numeric values in numeric metric columns will stop the
run with a validation error.

---

## 📁 Project Structure

```text
Email_report_app/
├── run_report.py           # Main application (use this!)
├── config.py               # Configuration & settings (uses env vars)
├── business_metrics.py     # KPI calculations & charts
├── ai_insights.py          # AI insights generation
├── automated_email.py      # Email sending with retry
├── test_api_connection.py  # OpenRouter connectivity diagnostics
├── utils/                  # Utility modules
│   ├── logger.py           # Centralized logging
│   ├── retry.py            # Retry mechanism
│   └── validators.py       # Input validation
├── tests/                  # Unit tests
├── data/
│   └── sample_data.csv     # Put your CSV files here
├── output/                 # Preview reports saved here
├── logs/                   # Log files (when enabled)
├── .env.example            # Environment variables template
├── *.bat                   # Double-click launchers
├── backend/                # FastAPI web API (see DEPLOYMENT.md)
├── frontend/                # React/Vite/Tailwind dashboard
└── worker/                  # Cloudflare Worker: serves frontend, proxies /api/*
```

---

## ⚙️ Configuration (Secure)

**All credentials must be set via environment variables** (not hardcoded):

### Step 1: Copy the template
```powershell
Copy-Item .env.example .env
```

### Step 2: Edit `.env` with your values
```env
# Required for sending email
EMAIL_SENDER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_RECIPIENTS=recipient1@example.com,recipient2@example.com

# Optional (AI-powered insights, off by default)
AI_ENABLED=false
OPENROUTER_API_KEY=sk-or-your-openrouter-key
LOG_LEVEL=INFO
```

AI is disabled by default so the app runs cleanly without network access —
reports use deterministic local insight text until `AI_ENABLED=true`.

### Step 3: Never commit `.env` to version control!

---

## 🔒 Security Features

- ✅ **No hardcoded credentials** - All secrets via environment variables
- ✅ **Input validation** - Email addresses, CSV data, config values
- ✅ **HTML sanitization** - Protection against XSS
- ✅ **Secure SMTP** - TLS/SSL encryption for email
- ✅ **Gitignore protection** - Sensitive files excluded

---

## 🔄 Retry Mechanism

The app automatically retries failed operations:

| Setting | Default | Description |
|---------|---------|-------------|
| `MAX_RETRIES` | 3 | Maximum retry attempts |
| `RETRY_BASE_DELAY` | 1.0s | Initial delay between retries |
| `RETRY_MAX_DELAY` | 60.0s | Maximum delay (exponential backoff) |

Retried operations:
- Email sending (SMTP errors)
- AI API calls (rate limits)

---

## 📝 Logging

Configure logging via environment variables:

```env
LOG_LEVEL=INFO          # DEBUG, INFO, WARNING, ERROR
LOG_TO_FILE=true        # Enable file logging
LOG_DIR=logs            # Log file directory
```

Log format: `2026-01-20 09:00:00 | INFO | module | Message`

---

## 🧪 Testing

Run all tests:
```powershell
python -m pytest tests/ -v
```

Or double-click: `RUN_TESTS.bat`

Run with coverage:
```powershell
python -m pytest tests/ --cov=. --cov-report=html
```

---

## 🤖 AI Features

The app generates AI-powered insights about your business metrics:
- Performance assessment
- Trend analysis
- Recommendations

**Setup AI (using OpenRouter - FREE DeepSeek R1):**
```env
AI_ENABLED=true
OPENROUTER_API_KEY=sk-or-your-openrouter-key
OPENROUTER_MODEL=deepseek/deepseek-r1-0528:free
```

Get your free API key at: https://openrouter.ai/keys

**No API key?** The app falls back to a locally cached Hugging Face model if
`USE_LOCAL_MODEL=true` and `requirements-ai.txt` is installed — otherwise it
uses deterministic local insight text.

### OpenRouter Diagnostics

If OpenRouter calls fail, run:
```powershell
python test_api_connection.py
```

It checks general internet access, DNS resolution for `openrouter.ai`,
endpoint reachability, and whether `OPENROUTER_API_KEY` is loaded — without
ever printing the key value.

---

## 📧 Email Setup (Gmail)

1. Enable 2-factor authentication in your Google account
2. Generate an App Password: https://myaccount.google.com/apppasswords
3. Add to your `.env` file:
   ```env
   EMAIL_SENDER=your-email@gmail.com
   EMAIL_PASSWORD=xxxx-xxxx-xxxx-xxxx
   ```

---

## Web App

The same report pipeline is also available as a browser app: a FastAPI
backend (`backend/`) wraps the modules above unchanged, a React/Vite frontend
(`frontend/`) provides the dashboard, and a Cloudflare Worker (`worker/`)
serves the frontend and proxies `/api/*` to the backend. See
[`DEPLOYMENT.md`](./DEPLOYMENT.md) for local development and deployment steps,
and [`docs/decisions.md`](./docs/decisions.md) for the reasoning behind how
it's structured.

---

## ℹ️ Notes

- **Preview first**: Use `PREVIEW_REPORT.bat` to test before sending
- **Schedule mode**: Runs continuously, sends at configured time
- **Dry-run**: Generates HTML without sending email
- **Logs**: Check `logs/` folder for detailed operation logs
- `.env` is ignored by git and should contain secrets only on your local machine

## Future Improvements

- Integrate multiple data sources such as APIs, CSV files, and databases
- Add richer report templates
- Automate the web app's report sending on a schedule (e.g. a Cloudflare Cron
  Trigger calling `POST /api/reports/send`)

## Author

Ihsan Hadhrami

- Portfolio: https://ihsanhadhrami.github.io/My-Portfolio/
- GitHub: https://github.com/ihsanhadhrami
