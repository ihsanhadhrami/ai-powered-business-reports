"""
AI Insights Module
Generates AI-powered analysis and email content for business reports.
Uses OpenRouter API (DeepSeek R1) with HuggingFace local fallback.
"""

import os
import requests
import json
from dotenv import load_dotenv
from config import AI_CONFIG

# Try to import transformers for a local open-source fallback
transformers_available = False
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
    transformers_available = True
except Exception:
    transformers_available = False

# Load environment variables from .env file
load_dotenv()

# OpenRouter API configuration
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

# Local model pipeline placeholder (lazy init)
_local_pipeline = None

def _init_local_pipeline(model_name=None):
    """Lazy initialize a HF text-generation pipeline for local fallback."""
    global _local_pipeline
    if _local_pipeline is not None:
        return _local_pipeline
    if not transformers_available:
        raise RuntimeError('transformers is not installed')

    model_name = model_name or AI_CONFIG.get('hf_model', 'distilgpt2')
    # distilgpt2 is small and reasonably fast on CPU; replace with a larger model if you have GPU
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    _local_pipeline = pipeline('text-generation', model=model, tokenizer=tokenizer, device=-1)
    return _local_pipeline

def chat_with_local_model(prompt, max_length=None):
    """Generate a response using a local HF model (causal LM).

    This is a simple fallback and won't follow chat role formatting like instruction-tuned models.
    """
    max_length = max_length or AI_CONFIG.get('hf_max_length', 100)
    gen_params = AI_CONFIG.get('generation_params', {})
    
    try:
        pipe = _init_local_pipeline()
        # `max_length` refers to total tokens (prompt + gen); keep modest defaults
        outputs = pipe(
            prompt, 
            max_length=max_length,
            truncation=True,
            do_sample=gen_params.get('do_sample', True),
            top_k=gen_params.get('top_k', 50),
            top_p=gen_params.get('top_p', 0.95),
            num_return_sequences=gen_params.get('num_return_sequences', 1)
        )
        if isinstance(outputs, list) and len(outputs) > 0:
            text = outputs[0].get('generated_text', '')
            # If the model echoes the prompt, strip the prompt prefix
            if text.startswith(prompt):
                return text[len(prompt):].strip()
            return text.strip()
        return ""
    except Exception as e:
        return f"Local model error: {e}"

def chat_with_openrouter(prompt, max_tokens=None, max_retries=3):
    """Send a chat request to OpenRouter API using DeepSeek R1.
    
    Args:
        prompt (str): The user prompt to send
        max_tokens (int): Maximum tokens for response
        max_retries (int): Maximum retry attempts for transient errors
    
    Returns:
        str: AI-generated response or error message
    """
    import time
    
    max_tokens = max_tokens or AI_CONFIG.get('openrouter_max_tokens', 150)
    model = AI_CONFIG.get('openrouter_model', 'deepseek/deepseek-r1-0528:free')
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": AI_CONFIG.get('site_url', 'http://localhost'),
        "X-Title": AI_CONFIG.get('site_name', 'Email Report App'),
    }
    
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
    }
    
    last_error = None
    for attempt in range(max_retries):
        try:
            response = requests.post(
                OPENROUTER_BASE_URL,
                headers=headers,
                data=json.dumps(payload),
                timeout=120  # Increased timeout for reasoning models
            )
            
            result = response.json()
            
            # Check for API errors in response body
            if 'error' in result:
                error_msg = result['error'].get('message', 'Unknown API error')
                error_code = result['error'].get('code', 0)
                # Retry on transient errors (502, 503, etc.)
                if error_code in [502, 503, 504] and attempt < max_retries - 1:
                    last_error = f"API error (code {error_code}): {error_msg}"
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                return f"OpenRouter API error: {error_msg}"
            
            response.raise_for_status()
            
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                if content:
                    return content.strip()
            return "No response generated from AI."
            
        except requests.exceptions.Timeout:
            last_error = "OpenRouter API request timed out."
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
        except requests.exceptions.RequestException as e:
            last_error = f"OpenRouter API error: {str(e)}"
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            return f"Error parsing OpenRouter response: {str(e)}"
    
    return last_error or "OpenRouter API failed after retries."


def chat_with_ai(prompt, max_tokens=None):
    """Primary chat function. Tries OpenRouter first (if available and key present), otherwise falls back to a local HF model.

    Environment overrides:
      - Set OPENROUTER_API_KEY to use OpenRouter (DeepSeek R1).
      - Set USE_LOCAL_MODEL=1 to force local model usage.
    """
    max_tokens = max_tokens or AI_CONFIG.get('openrouter_max_tokens', 150)
    use_local = os.getenv('USE_LOCAL_MODEL', str(AI_CONFIG.get('use_local_model', False))) in ['1', 'true', 'True']

    # If forced to use local model
    if use_local:
        return chat_with_local_model(prompt, max_length=max_tokens)

    # Try OpenRouter first if API key exists
    if OPENROUTER_API_KEY:
        result = chat_with_openrouter(prompt, max_tokens)
        # Check if result is an error and we have fallback available
        if ('error' in result.lower() or 'timed out' in result.lower()) and transformers_available:
            fallback = chat_with_local_model(prompt, max_length=max_tokens)
            return f"(OpenRouter failed: {result})\n\n[FALLBACK - Local model]\n{fallback}"
        return result

    # No OpenRouter API key; use local if possible
    if transformers_available:
        return chat_with_local_model(prompt, max_length=max_tokens)

    return "No backend available: neither OpenRouter API key nor local transformers are usable."

def generate_metric_insights(kpis_dict):
    """Generate AI-powered insights based on business metrics.
    
    Args:
        kpis_dict (dict): Dictionary of KPIs from BusinessMetrics.calculate_kpis()
    
    Returns:
        str: AI-generated analysis and insights
    """
    # Format KPIs into a readable prompt
    kpi_summary = "Business KPIs:\n"
    for key, value in kpis_dict.items():
        if isinstance(value, float):
            kpi_summary += f"- {key.replace('_', ' ').title()}: {value:,.2f}\n"
        else:
            kpi_summary += f"- {key.replace('_', ' ').title()}: {value}\n"
    
    prompt = f"""Analyze these business metrics and provide a brief executive summary with actionable insights:

{kpi_summary}

Provide:
1. Overall performance assessment
2. Key trends and patterns
3. Areas of concern (if any)
4. Actionable recommendations

Keep it concise and business-focused."""
    
    return chat_with_ai(prompt, max_tokens=500)


def generate_email_content_from_metrics(kpis_dict, report_title="Business Report"):
    """Generate AI-powered email content based on business metrics.
    
    Args:
        kpis_dict (dict): Dictionary of KPIs from BusinessMetrics.calculate_kpis()
        report_title (str): Title for the report
    
    Returns:
        dict: Dictionary with 'subject' and 'body' for email sending
    """
    insights = generate_metric_insights(kpis_dict)
    
    # Generate AI subject line with fallback
    subject_prompt = f"Create a professional email subject line for a business report titled '{report_title}' with metrics. Keep it under 60 characters."
    subject = chat_with_ai(subject_prompt, max_tokens=30).strip()
    
    # Use fallback subject if AI failed (error messages contain 'failed' or 'error')
    if 'failed' in subject.lower() or 'error' in subject.lower() or len(subject) > 100:
        subject = report_title  # Use the report title directly as fallback
    
    # Format KPIs for HTML display
    kpi_html = '<div class="kpi-grid">'
    for key, value in list(kpis_dict.items())[:6]:  # Show first 6 KPIs
        display_key = key.replace('_', ' ').title()
        if isinstance(value, float):
            display_value = f"{value:,.2f}"
        else:
            display_value = str(value)
        kpi_html += f'<div class="kpi-card"><h3>{display_key}</h3><p>{display_value}</p></div>'
    kpi_html += '</div>'
    
    body = f"""
    <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #2c3e50; }}
                .container {{ max-width: 800px; margin: auto; background: #fff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }}
                .header {{ background: linear-gradient(135deg, #2E86C1 0%, #3498db 100%); color: white; padding: 25px 20px; text-align: center; }}
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
                    <h2>{report_title}</h2>
                </div>
                <div class="content">
                    <h3>Performance Metrics</h3>
                    {kpi_html}
                    
                    <div class="insights">
                        <h3>📊 AI-Generated Insights</h3>
                        <p>{insights}</p>
                    </div>
                </div>
                <div class="footer">
                    <p>Report generated on: {__import__('datetime').datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                    <p style="color: #94a3b8; font-size: 12px;">This is an automated report with AI-powered analysis.</p>
                </div>
            </div>
        </body>
    </html>
    """
    
    return {
        'subject': subject,
        'body': body,
        'insights': insights
    }
