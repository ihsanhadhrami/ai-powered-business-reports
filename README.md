# Automated Email Report (Simple, Impactful)

This project generates an automated business performance email report with KPIs, interactive charts, and AI-powered insights.

## 🚀 Quick Start (Windows)

### **Option 1: Double-Click to Run (Easiest)**

1. **Install dependencies** (first time only):
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements_updated.txt
   ```

2. **Configure your settings** in `config.py`:
   - Email credentials (SMTP)
   - Recipients
   - Report schedule

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
2. Update `config.py`:
   ```python
   DATA_SOURCE = {
       "type": "csv",
       "path": "data/your_data.csv"  # Change to your filename
   }
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

---

## 📁 Project Structure

```
Email_report_app/
├── run_report.py           # Main application (use this!)
├── config.py               # Configuration & settings (uses env vars)
├── business_metrics.py     # KPI calculations & charts
├── ai_insights.py          # AI insights generation
├── automated_email.py      # Email sending with retry
├── utils/                  # Utility modules
│   ├── logger.py           # Centralized logging
│   ├── retry.py            # Retry mechanism
│   └── validators.py       # Input validation
├── tests/                  # Unit tests
│   ├── test_business_metrics.py
│   ├── test_validators.py
│   ├── test_retry.py
│   └── test_integration.py
├── data/
│   └── sample_data.csv     # Put your CSV files here
├── output/                 # Preview reports saved here
├── logs/                   # Log files (when enabled)
├── .env.example            # Environment variables template
└── *.bat                   # Double-click launchers
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
# Required
EMAIL_SENDER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_RECIPIENTS=recipient1@example.com,recipient2@example.com

# Optional (AI-powered insights)
OPENROUTER_API_KEY=sk-or-your-openrouter-key
LOG_LEVEL=INFO
```

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
OPENROUTER_API_KEY=sk-or-your-openrouter-key
OPENROUTER_MODEL=deepseek/deepseek-r1-0528:free
```

Get your free API key at: https://openrouter.ai/keys

**No API key?** The app falls back to a local HuggingFace model.

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

## ℹ️ Notes

- **Preview first**: Use `PREVIEW_REPORT.bat` to test before sending
- **Schedule mode**: Runs continuously, sends at configured time
- **Dry-run**: Generates HTML without sending email
- **Logs**: Check `logs/` folder for detailed operation logs

