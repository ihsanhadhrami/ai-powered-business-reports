# AI Integration Guide

AI support is optional. The app now runs cleanly without OpenRouter, Hugging Face,
or network access.

## Default Local Behavior

With this setting:

```env
AI_ENABLED=false
```

`ai_insights.py` generates deterministic local insight text from the KPI values.
No external API calls are made.

## OpenRouter Mode

Set:

```env
AI_ENABLED=true
OPENROUTER_API_KEY=your-openrouter-key
OPENROUTER_MODEL=deepseek/deepseek-r1-0528:free
AI_REQUEST_TIMEOUT=30
```

OpenRouter calls happen in `chat_with_openrouter()` and are used by
`generate_metric_insights()` and the optional AI subject generator.

If OpenRouter fails, the app falls back to deterministic local insights instead
of embedding exception text in the report.

## Local Hugging Face Mode

Install optional dependencies:

```powershell
pip install -r requirements-ai.txt
```

Set:

```env
AI_ENABLED=true
USE_LOCAL_MODEL=true
HF_MODEL=distilgpt2
```

The local model loader uses `local_files_only=True`, so report generation will not
try to download model files at runtime. Cache the model separately before enabling
this mode.

## Report Flow

```text
CSV data
  -> validate_csv_data()
  -> BusinessMetrics.calculate_kpis()
  -> generate_metric_insights()
  -> generate_email_content_from_metrics()
  -> save_html_report() or send_email()
```

## Failure Handling

- AI disabled: deterministic local insights.
- OpenRouter unavailable: deterministic local insights.
- Hugging Face unavailable or uncached: deterministic local insights.
- AI errors are not inserted into the HTML report.
