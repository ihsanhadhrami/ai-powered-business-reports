"""
AI and local insight generation for business reports.

Network-backed AI is optional. By default the app uses deterministic local
insights so dry-runs are fast and clean on machines without API/network access.
Set AI_ENABLED=true in .env to use OpenRouter or the local Hugging Face backend.
"""

import html
import json
import os
from typing import Any

import requests
from dotenv import load_dotenv

from config import AI_CONFIG

try:
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

    transformers_available = True
except Exception:
    transformers_available = False

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

_local_pipeline = None


def _env_truthy(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def ai_enabled() -> bool:
    """Return whether network/local model AI generation is enabled."""
    return _env_truthy("AI_ENABLED", AI_CONFIG.get("enabled", False))


def _is_error_text(text: str) -> bool:
    lowered = text.lower()
    return any(
        marker in lowered
        for marker in [
            "error",
            "failed",
            "timed out",
            "traceback",
            "exception",
            "httpsconnectionpool",
            "no backend available",
        ]
    )


def _init_local_pipeline(model_name: str | None = None):
    """Lazy initialize a Hugging Face text-generation pipeline."""
    global _local_pipeline
    if _local_pipeline is not None:
        return _local_pipeline
    if not transformers_available:
        raise RuntimeError("transformers is not installed")

    model_name = model_name or AI_CONFIG.get("hf_model", "distilgpt2")
    tokenizer = AutoTokenizer.from_pretrained(model_name, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(model_name, local_files_only=True)
    _local_pipeline = pipeline("text-generation", model=model, tokenizer=tokenizer, device=-1)
    return _local_pipeline


def chat_with_local_model(prompt: str, max_length: int | None = None) -> str:
    """Generate a response using a locally cached Hugging Face model."""
    max_length = max_length or AI_CONFIG.get("hf_max_length", 100)
    gen_params = AI_CONFIG.get("generation_params", {})

    pipe = _init_local_pipeline()
    outputs = pipe(
        prompt,
        max_length=max_length,
        truncation=True,
        do_sample=gen_params.get("do_sample", True),
        top_k=gen_params.get("top_k", 50),
        top_p=gen_params.get("top_p", 0.95),
        num_return_sequences=gen_params.get("num_return_sequences", 1),
    )
    if isinstance(outputs, list) and outputs:
        text = outputs[0].get("generated_text", "")
        if text.startswith(prompt):
            return text[len(prompt) :].strip()
        return text.strip()
    return ""


def chat_with_openrouter(prompt: str, max_tokens: int | None = None, max_retries: int = 1) -> str:
    """Send a chat request to OpenRouter."""
    import time

    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set")

    max_tokens = max_tokens or AI_CONFIG.get("openrouter_max_tokens", 150)
    model = AI_CONFIG.get("openrouter_model", "deepseek/deepseek-r1-0528:free")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": AI_CONFIG.get("site_url", "http://localhost"),
        "X-Title": AI_CONFIG.get("site_name", "Email Report App"),
    }

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
    }

    last_error = None
    for attempt in range(max_retries):
        try:
            response = requests.post(
                OPENROUTER_BASE_URL,
                headers=headers,
                data=json.dumps(payload),
                timeout=AI_CONFIG.get("request_timeout", 30),
            )
            result = response.json()

            if "error" in result:
                error_msg = result["error"].get("message", "Unknown API error")
                error_code = result["error"].get("code", 0)
                if error_code in [502, 503, 504] and attempt < max_retries - 1:
                    last_error = f"API error (code {error_code}): {error_msg}"
                    time.sleep(2**attempt)
                    continue
                raise RuntimeError(f"OpenRouter API error: {error_msg}")

            response.raise_for_status()

            if result.get("choices"):
                content = result["choices"][0]["message"]["content"]
                if content:
                    return content.strip()
            raise RuntimeError("No response generated from AI")
        except requests.exceptions.Timeout:
            last_error = "OpenRouter API request timed out"
            if attempt < max_retries - 1:
                time.sleep(2**attempt)
                continue
        except requests.exceptions.RequestException as e:
            last_error = f"OpenRouter API error: {e}"
            if attempt < max_retries - 1:
                time.sleep(2**attempt)
                continue
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            raise RuntimeError(f"Error parsing OpenRouter response: {e}") from e

    raise RuntimeError(last_error or "OpenRouter API failed after retries")


def chat_with_ai(prompt: str, max_tokens: int | None = None) -> str:
    """Generate text with the configured AI backend."""
    if not ai_enabled():
        raise RuntimeError("AI is disabled. Set AI_ENABLED=true to use an AI backend.")

    max_tokens = max_tokens or AI_CONFIG.get("openrouter_max_tokens", 150)
    use_local = _env_truthy("USE_LOCAL_MODEL", AI_CONFIG.get("use_local_model", False))

    if use_local:
        return chat_with_local_model(prompt, max_length=max_tokens)

    if OPENROUTER_API_KEY:
        return chat_with_openrouter(prompt, max_tokens=max_tokens)

    if transformers_available:
        return chat_with_local_model(prompt, max_length=max_tokens)

    raise RuntimeError("No AI backend is available")


def _format_metric_name(key: str) -> str:
    return key.replace("_", " ").title()


def _get_number(kpis: dict[str, Any], key: str) -> float | None:
    value = kpis.get(key)
    return value if isinstance(value, (int, float)) else None


def generate_local_insights(kpis_dict: dict[str, Any]) -> str:
    """Generate deterministic local insights without external API calls."""
    lines = []

    total_revenue = _get_number(kpis_dict, "total_revenue")
    avg_revenue = _get_number(kpis_dict, "avg_daily_revenue")
    revenue_growth = _get_number(kpis_dict, "revenue_growth")
    sales_growth = _get_number(kpis_dict, "sales_growth")
    customer_growth = _get_number(kpis_dict, "customer_growth")

    if total_revenue is not None:
        lines.append(f"Total revenue is ${total_revenue:,.2f}.")
    if avg_revenue is not None:
        lines.append(f"Average daily revenue is ${avg_revenue:,.2f}.")

    growth_parts = []
    for label, value in [
        ("revenue", revenue_growth),
        ("sales", sales_growth),
        ("customer", customer_growth),
    ]:
        if value is not None:
            direction = "up" if value > 0 else "down" if value < 0 else "flat"
            growth_parts.append(f"{label} growth is {direction} at {value:+.2f}%")

    if growth_parts:
        lines.append("; ".join(growth_parts) + ".")

    negative_growth = [
        label
        for label, value in [
            ("revenue", revenue_growth),
            ("sales", sales_growth),
            ("customer", customer_growth),
        ]
        if value is not None and value < 0
    ]
    if negative_growth:
        lines.append(f"Review the drivers behind declining {', '.join(negative_growth)}.")
    else:
        lines.append("No negative growth indicators were detected in the tracked KPIs.")

    lines.append("Recommended next step: compare these results with the prior reporting period and investigate the highest-impact metric first.")
    return " ".join(lines)


def generate_metric_insights(kpis_dict: dict[str, Any]) -> str:
    """Generate insights from business KPIs."""
    if not ai_enabled():
        return generate_local_insights(kpis_dict)

    kpi_summary = "Business KPIs:\n"
    for key, value in kpis_dict.items():
        if isinstance(value, float):
            kpi_summary += f"- {_format_metric_name(key)}: {value:,.2f}\n"
        else:
            kpi_summary += f"- {_format_metric_name(key)}: {value}\n"

    prompt = f"""Analyze these business metrics and provide a brief executive summary with actionable insights:

{kpi_summary}

Provide:
1. Overall performance assessment
2. Key trends and patterns
3. Areas of concern (if any)
4. Actionable recommendations

Keep it concise and business-focused."""

    try:
        result = chat_with_ai(prompt, max_tokens=500)
        if result and not _is_error_text(result):
            return result
    except Exception:
        pass

    return generate_local_insights(kpis_dict)


def _generate_subject(kpis_dict: dict[str, Any], report_title: str) -> str:
    if not ai_enabled():
        return report_title

    prompt = (
        f"Create a professional email subject line for a business report titled "
        f"'{report_title}' with metrics. Keep it under 60 characters."
    )
    try:
        subject = chat_with_ai(prompt, max_tokens=30).strip().strip('"')
        if subject and len(subject) <= 100 and not _is_error_text(subject):
            return subject
    except Exception:
        pass
    return report_title


def generate_email_content_from_metrics(
    kpis_dict: dict[str, Any],
    report_title: str = "Business Report",
    insights: str | None = None,
) -> dict[str, str]:
    """Generate HTML email content based on business metrics."""
    insights = insights if insights is not None else generate_metric_insights(kpis_dict)
    subject = _generate_subject(kpis_dict, report_title)

    kpi_cards = []
    for key, value in list(kpis_dict.items())[:6]:
        display_key = html.escape(_format_metric_name(key))
        display_value = f"{value:,.2f}" if isinstance(value, float) else str(value)
        kpi_cards.append(
            f'<div class="kpi-card"><h3>{display_key}</h3><p>{html.escape(display_value)}</p></div>'
        )
    kpi_html = '<div class="kpi-grid">' + "".join(kpi_cards) + "</div>"

    safe_title = html.escape(report_title)
    safe_insights = html.escape(insights).replace("\n", "<br>")

    body = f"""<!doctype html>
<html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #2c3e50; background: #f8fafc; padding: 20px; }}
            .container {{ max-width: 800px; margin: auto; background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.08); }}
            .header {{ background: #2E86C1; color: white; padding: 25px 20px; text-align: center; }}
            .header h2 {{ margin: 0; font-size: 24px; font-weight: 600; }}
            .content {{ padding: 30px; }}
            .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
            .kpi-card {{ background: #f8fafc; padding: 20px; border-radius: 8px; text-align: center; border: 1px solid #e1e8ed; }}
            .kpi-card h3 {{ margin: 0; font-size: 14px; color: #64748b; }}
            .kpi-card p {{ margin: 10px 0 0 0; font-size: 20px; font-weight: 600; color: #2c3e50; }}
            .insights {{ background: #e3f2fd; padding: 20px; border-radius: 8px; border-left: 4px solid #2E86C1; margin: 20px 0; }}
            .footer {{ text-align: center; padding: 20px; font-size: 13px; color: #64748b; background: #f8fafc; border-top: 1px solid #e2e8f0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>{safe_title}</h2>
            </div>
            <div class="content">
                <h3>Performance Metrics</h3>
                {kpi_html}

                <div class="insights">
                    <h3>Report Insights</h3>
                    <p>{safe_insights}</p>
                </div>
            </div>
            <div class="footer">
                <p>Report generated on: {__import__('datetime').datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                <p style="color: #94a3b8; font-size: 12px;">This is an automated report.</p>
            </div>
        </div>
    </body>
</html>
"""

    return {
        "subject": subject,
        "body": body,
        "insights": insights,
    }
