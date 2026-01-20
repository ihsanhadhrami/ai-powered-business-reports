## AI Integration Summary

This document describes the integration of AI capabilities across the Email Report App modules.

### 📊 Modules Overview

#### 1. **ai_insights.py**
AI-powered insights generator with OpenRouter (DeepSeek R1) and Hugging Face fallback support.

**Functions:**
- `generate_metric_insights(kpis_dict)` - Generate AI analysis based on business metrics
- `generate_email_content_from_metrics(kpis_dict, report_title)` - Create AI-powered email content

#### 2. **business_metrics.py**
Calculates business KPIs (Revenue, Sales, Customers) with trend analysis.

**Key Methods:**
- `calculate_kpis()` - Returns dictionary of key metrics
- `generate_trend_chart()` - Creates interactive Plotly charts
- `generate_summary_html()` - Generates HTML report fragment

#### 3. **automated_email.py**
Sends formatted HTML emails with attachments using Gmail SMTP.

**Key Functions:**
- `send_email(subject, body, recipients, attachments)` - Core email sending
- `attach_file(msg, filepath)` - Attach files to emails

#### 4. **run_report.py** (Main Entry Point)
Orchestrates the complete workflow - use this to run the app.

---

### 🔄 Integration Flow

```
Business Data (CSV/Database)
    ↓
BusinessMetrics (Calculate KPIs)
    ↓
AI Chatbot (Generate Insights)
    ↓
Email Generator (Create HTML)
    ↓
Automated Email (Send via SMTP)
```

---

### 🚀 Usage Examples

#### Example 1: Generate Insights from KPIs
```python
from business_metrics import BusinessMetrics
from ai_insights import generate_metric_insights
import pandas as pd

# Calculate KPIs
df = pd.read_csv('data/business_data.csv')
metrics = BusinessMetrics(df)
kpis = metrics.calculate_kpis()

# Get AI insights
insights = generate_metric_insights(kpis)
print(insights)
```

#### Example 2: Run the Complete Workflow
```bash
# Preview report (no email sent)
python run_report.py --dry-run

# Send email now
python run_report.py

# Or double-click: QUICK_START.bat
```

---

### ⚙️ Configuration

All settings are in `config.py`:

**AI Settings:**
```python
AI_CONFIG = {
    "openrouter_model": "deepseek/deepseek-r1-0528:free",
    "openrouter_max_tokens": 150,
    "site_url": "http://localhost",
    "site_name": "Email Report App",
    "hf_model": "distilgpt2",
    "hf_max_length": 100,
    "generation_params": {...},
    "use_local_model": False
}
```

**Email Settings:**
```python
EMAIL_SENDER = "your-email@gmail.com"
EMAIL_PASSWORD = "your-app-password"
EMAIL_RECIPIENTS = ["recipient@company.com"]
```

---

### 🔑 Features

✅ **AI Integration:**
- Automatic metric analysis and insights
- AI-generated email subjects and content
- Smart fallback from OpenRouter to local models
- Uses DeepSeek R1 (FREE tier) via OpenRouter
- Configurable model parameters

✅ **Business Metrics:**
- Revenue, sales, and customer tracking
- Growth rate calculations
- Moving average trend analysis
- Interactive charts

✅ **Email Automation:**
- HTML-formatted reports
- File attachments
- SSL/TLS security
- Customizable templates

✅ **Configuration Management:**
- All hardcoded values removed
- Environment variable support
- Centralized config file
- Easy customization

---

### 📝 Dependencies

Add these to `requirements_updated.txt`:
```
requests>=2.28.0
transformers>=4.30.0
pandas>=1.5.0
plotly>=5.0.0
python-dotenv>=1.0.0
```

---

### 🛠️ Best Practices

1. **Set your OpenRouter API key** in `.env` file:
   ```
   OPENROUTER_API_KEY=your-api-key-here
   ```
   Get your free key at: https://openrouter.ai/keys

2. **Use environment variables** for sensitive data (passwords, API keys)

3. **Test locally** before scheduling automated jobs:
   ```bash
   python integrated_workflow.py
   ```

4. **Monitor AI output** as the model improves over time

5. **Customize prompts** in `generate_metric_insights()` for your use case

---

### 🐛 Troubleshooting

**OpenRouter API errors:**
- Verify `OPENROUTER_API_KEY` is set in `.env`
- Get your free key at: https://openrouter.ai/keys
- Falls back to local model automatically

**Email sending fails:**
- Enable "Less secure app access" for Gmail
- Use app-specific password (not regular password)
- Verify `EMAIL_SENDER` and `EMAIL_PASSWORD` in config.py

**Missing dependencies:**
- Install: `pip install -r requirements_updated.txt`
- For Hugging Face models: `pip install transformers`

---

### 📧 Example Generated Email

The integrated workflow generates professional emails with:
- **Subject:** AI-generated, concise and relevant
- **Header:** Gradient background with report title
- **Metrics:** Interactive KPI cards showing current values
- **Insights:** AI-generated analysis with recommendations
- **Footer:** Timestamp and automated report notice
- **Style:** Responsive, modern, mobile-friendly design

---

## Summary

The integration provides a complete end-to-end solution for:
1. **Calculate** business metrics automatically
2. **Analyze** using AI to extract insights
3. **Generate** professional reports with AI content
4. **Distribute** via automated email

All with **zero hardcoded values** and **full configuration management**.
