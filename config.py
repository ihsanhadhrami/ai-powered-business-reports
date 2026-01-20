"""
Configuration settings for the email report automation.

SECURITY NOTE: 
- All sensitive credentials should be set via environment variables
- Never commit actual credentials to version control
- Use a .env file for local development (added to .gitignore)
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_env(key: str, default: str = None, required: bool = False) -> str:
    """
    Get environment variable with optional default and required flag.
    
    Args:
        key: Environment variable name
        default: Default value if not set
        required: If True, raises error when not set
    
    Returns:
        Environment variable value
    
    Raises:
        ValueError: If required variable is not set
    """
    value = os.getenv(key, default)
    if required and not value:
        raise ValueError(f"Required environment variable '{key}' is not set")
    return value


# =============================================================================
# EMAIL CONFIGURATION (Set via environment variables)
# =============================================================================

# Email sender credentials - MUST be set via environment variables
EMAIL_SENDER = get_env('EMAIL_SENDER', '')
EMAIL_PASSWORD = get_env('EMAIL_PASSWORD', '')
SMTP_SERVER = get_env('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(get_env('SMTP_PORT', '587'))

# Recipients - can be comma-separated in env var or set here
_recipients_env = get_env('EMAIL_RECIPIENTS', '')
EMAIL_RECIPIENTS = [
    email.strip() for email in _recipients_env.split(',') if email.strip()
] if _recipients_env else [
    # Default recipients (update these)
    "ihsanhadhrami@yahoo.com",
]

# Report Settings
REPORT_FREQUENCY = get_env('REPORT_FREQUENCY', 'daily')  # Options: daily, weekly, monthly
REPORT_TIME = get_env('REPORT_TIME', '09:00')  # 24-hour format

# Data Source Configuration
DATA_SOURCE = {
    "type": get_env('DATA_SOURCE_TYPE', 'csv'),
    "path": get_env('DATA_SOURCE_PATH', 'data/sample_data.csv')
}

# =============================================================================
# AI CONFIGURATION
# =============================================================================

AI_CONFIG = {
    # OpenRouter settings (DeepSeek R1)
    "openrouter_model": get_env('OPENROUTER_MODEL', 'deepseek/deepseek-r1-0528:free'),
    "openrouter_max_tokens": int(get_env('OPENROUTER_MAX_TOKENS', '150')),
    
    # Site info for OpenRouter rankings (optional)
    "site_url": get_env('SITE_URL', 'http://localhost'),
    "site_name": get_env('SITE_NAME', 'Email Report App'),
    
    # Local model settings (Hugging Face)
    "hf_model": get_env('HF_MODEL', 'distilgpt2'),
    "hf_max_length": int(get_env('HF_MAX_LENGTH', '100')),
    
    # Generation parameters for local models
    "generation_params": {
        "do_sample": True,
        "top_k": 50,
        "top_p": 0.95,
        "num_return_sequences": 1
    },
    
    # Fallback behavior
    "use_local_model": get_env('USE_LOCAL_MODEL', 'false').lower() == 'true',
}

# =============================================================================
# RETRY CONFIGURATION
# =============================================================================

RETRY_CONFIG = {
    "max_retries": int(get_env('MAX_RETRIES', '3')),
    "base_delay": float(get_env('RETRY_BASE_DELAY', '1.0')),
    "max_delay": float(get_env('RETRY_MAX_DELAY', '60.0')),
}

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

LOG_CONFIG = {
    "level": get_env('LOG_LEVEL', 'INFO'),
    "to_file": get_env('LOG_TO_FILE', 'false').lower() == 'true',
    "log_dir": get_env('LOG_DIR', 'logs'),
}

# Report Template (interactive, modern design)
EMAIL_TEMPLATE = """
<html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <style>
            /* Modern Reset and Base Styles */
            body { 
                font-family: 'Segoe UI', Arial, sans-serif;
                line-height: 1.6;
                color: #2c3e50;
                margin: 0;
                padding: 20px;
                background: #f8fafc;
            }

            /* Container with subtle shadow */
            .container { 
                max-width: 800px; 
                margin: auto; 
                background: #fff; 
                border-radius: 12px; 
                overflow: hidden;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }

            /* Modern gradient header */
            .header { 
                background: linear-gradient(135deg, #2E86C1 0%, #3498db 100%);
                color: white;
                padding: 25px 20px;
                text-align: center;
            }
            
            .header h2 {
                margin: 0;
                font-size: 24px;
                font-weight: 600;
                text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
            }

            /* Content area with better spacing */
            .content { 
                padding: 30px; 
                color: #2c3e50;
            }

            /* Interactive Cards */
            .card-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin: 25px 0;
            }

            .card {
                background: #fff;
                border-radius: 8px;
                padding: 20px;
                transition: transform 0.2s, box-shadow 0.2s;
                border: 1px solid #e1e8ed;
                cursor: pointer;
            }

            .card:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            }

            /* Modern Buttons */
            .button {
                display: inline-block;
                padding: 12px 24px;
                background: #3498db;
                color: white;
                text-decoration: none;
                border-radius: 6px;
                font-weight: 500;
                margin: 10px 0;
                text-align: center;
                transition: background 0.3s;
            }

            .button:hover {
                background: #2980b9;
            }

            /* Status Indicators */
            .status {
                display: inline-block;
                padding: 6px 12px;
                border-radius: 20px;
                font-size: 14px;
                font-weight: 500;
            }

            .status.success { background: #e3fcef; color: #0a8554; }
            .status.warning { background: #fff8e6; color: #cb8e12; }
            .status.error { background: #fee7e7; color: #c53030; }

            /* Modern Table Styles */
            table { 
                width: 100%; 
                border-collapse: separate;
                border-spacing: 0;
                margin: 20px 0;
                background: #fff;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            }

            th { 
                background: #f8fafc;
                padding: 12px 15px;
                text-align: left;
                font-weight: 600;
                color: #2c3e50;
                border-bottom: 2px solid #e2e8f0;
            }

            td { 
                padding: 12px 15px;
                border-bottom: 1px solid #e2e8f0;
            }

            tr:last-child td { border-bottom: none; }
            tr:hover { background: #f8fafc; }

            /* KPI Cards with animations */
            .kpi-grid { 
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                gap: 20px;
                margin: 25px 0;
            }

            .kpi-card {
                background: #fff;
                padding: 20px;
                border-radius: 8px;
                text-align: center;
                transition: transform 0.2s;
                border: 1px solid #e1e8ed;
            }

            .kpi-card:hover {
                transform: translateY(-2px);
            }

            .kpi-card h3 { 
                margin: 0; 
                font-size: 14px;
                color: #64748b;
                font-weight: 500;
            }

            .kpi-card p { 
                margin: 10px 0 0 0;
                font-size: 24px;
                font-weight: 600;
                color: #2c3e50;
            }

            /* Modern Footer */
            .footer { 
                text-align: center;
                padding: 20px;
                font-size: 13px;
                color: #64748b;
                background: #f8fafc;
                border-top: 1px solid #e2e8f0;
            }

            /* Responsive Images */
            img {
                max-width: 100%;
                height: auto;
                border-radius: 8px;
                margin: 10px 0;
            }

            /* Chart Container */
            .chart-container {
                margin: 25px 0;
                padding: 15px;
                background: #fff;
                border-radius: 8px;
                border: 1px solid #e1e8ed;
            }

            /* Alert Boxes */
            .alert {
                padding: 15px 20px;
                border-radius: 8px;
                margin: 15px 0;
                display: flex;
                align-items: center;
                gap: 10px;
            }

            .alert.info { background: #e3f2fd; color: #1565c0; }
            .alert.success { background: #e8f5e9; color: #2e7d32; }
            .alert.warning { background: #fff3e0; color: #ef6c00; }
            .alert.error { background: #ffebee; color: #c62828; }

            /* Mobile Responsiveness */
            @media (max-width: 640px) {
                body { padding: 10px; }
                .container { border-radius: 8px; }
                .content { padding: 20px; }
                .kpi-grid { grid-template-columns: 1fr; }
                .card-grid { grid-template-columns: 1fr; }
                .button { display: block; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>{title}</h2>
            </div>
            <div class="content">
                {content}
            </div>
            <div class="footer">
                <p>Report generated on: {timestamp}</p>
                <p style="color: #94a3b8; font-size: 12px;">This is an automated report. Please do not reply to this email.</p>
            </div>
        </div>
    </body>
</html>
"""
