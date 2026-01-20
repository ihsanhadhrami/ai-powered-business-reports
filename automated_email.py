"""
Automated Email Sending Module

Provides secure email sending functionality with:
- Retry mechanisms for reliability
- Input validation for security
- Proper logging for monitoring
"""

import smtplib
import ssl
import os
import mimetypes
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email.utils import formatdate
from datetime import datetime
from typing import List, Optional, Union

import config
from utils.logger import setup_logger
from utils.retry import retry_with_backoff
from utils.validators import validate_email_list, ValidationError

# Initialize logger
logger = setup_logger(__name__)


def attach_file(msg: MIMEMultipart, filepath: str) -> bool:
    """
    Attach a file to the email message based on its type.
    
    Args:
        msg: The email message to attach to
        filepath: Path to the file to attach
    
    Returns:
        True if attachment succeeded, False otherwise
    """
    if not os.path.isfile(filepath):
        logger.warning(f"Attachment file not found: {filepath}")
        return False

    # Guess the content type based on the file's extension
    ctype, encoding = mimetypes.guess_type(filepath)
    if ctype is None or encoding is not None:
        ctype = 'application/octet-stream'
    
    maintype, subtype = ctype.split('/', 1)
    
    try:
        with open(filepath, 'rb') as f:
            file_content = f.read()
            
        if maintype == 'text':
            part = MIMEText(file_content.decode(), _subtype=subtype)
        elif maintype == 'image':
            part = MIMEImage(file_content, _subtype=subtype)
        elif maintype == 'application' and subtype == 'pdf':
            part = MIMEApplication(file_content, _subtype='pdf')
        else:
            part = MIMEBase(maintype, subtype)
            part.set_payload(file_content)
            from email import encoders
            encoders.encode_base64(part)
        
        filename = os.path.basename(filepath)
        part.add_header('Content-Disposition', 'attachment', filename=filename)
        msg.attach(part)
        logger.info(f"Successfully attached: {filename}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to attach {filepath}: {e}")
        return False


def _validate_email_config() -> bool:
    """Validate email configuration before sending."""
    if not config.EMAIL_SENDER:
        logger.error("EMAIL_SENDER is not configured. Set via environment variable.")
        return False
    
    if not config.EMAIL_PASSWORD:
        logger.error("EMAIL_PASSWORD is not configured. Set via environment variable.")
        return False
    
    return True


@retry_with_backoff(
    max_retries=config.RETRY_CONFIG.get('max_retries', 3),
    base_delay=config.RETRY_CONFIG.get('base_delay', 1.0),
    max_delay=config.RETRY_CONFIG.get('max_delay', 60.0),
    exceptions=(smtplib.SMTPException, ConnectionError, TimeoutError)
)
def _send_email_with_retry(
    smtp_server: str,
    smtp_port: int,
    sender: str,
    password: str,
    recipients: List[str],
    msg: MIMEMultipart
) -> bool:
    """
    Internal function to send email with retry mechanism.
    
    Raises exceptions to trigger retry decorator.
    """
    context = ssl.create_default_context()
    
    if smtp_port == 465:  # SSL
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context, timeout=30) as server:
            server.login(sender, password)
            server.sendmail(sender, recipients, msg.as_string())
    else:  # TLS
        with smtplib.SMTP(smtp_server, smtp_port, timeout=30) as server:
            server.starttls(context=context)
            server.login(sender, password)
            server.sendmail(sender, recipients, msg.as_string())
    
    return True


def send_email(
    subject: Optional[str] = None,
    body: Optional[str] = None,
    recipients: Optional[List[str]] = None,
    attachments: Optional[Union[str, List[str]]] = None
) -> bool:
    """
    Send an email using configuration from config.py with retry mechanism.
    
    Args:
        subject: Email subject. Defaults to timestamp if None.
        body: Email body (can be HTML). Defaults to empty template if None.
        recipients: List of recipients. Defaults to config recipients if None.
        attachments: File path(s) to attach to the email.
    
    Returns:
        True if email was sent successfully, False otherwise
    """
    # Validate configuration
    if not _validate_email_config():
        return False
    
    try:
        sender = config.EMAIL_SENDER
        password = config.EMAIL_PASSWORD
        smtp_server = config.SMTP_SERVER
        smtp_port = config.SMTP_PORT
        recipients = recipients or config.EMAIL_RECIPIENTS
        
        # Validate recipients
        try:
            recipients = validate_email_list(recipients)
        except ValidationError as e:
            logger.error(f"Invalid recipients: {e}")
            return False
        
        logger.info(f"Preparing email to {len(recipients)} recipient(s)")
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = sender
        msg['To'] = ', '.join(recipients)
        msg['Subject'] = subject or f"Automated Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        msg['Date'] = formatdate(localtime=True)
        
        # Use template from config if no body provided
        if body is None:
            body = config.EMAIL_TEMPLATE
        
        msg.attach(MIMEText(body, 'html'))
        
        # Attach files if provided
        if attachments:
            if isinstance(attachments, str):
                attach_file(msg, attachments)
            elif isinstance(attachments, (list, tuple)):
                for filepath in attachments:
                    attach_file(msg, filepath)
        
        # Send with retry
        _send_email_with_retry(
            smtp_server=smtp_server,
            smtp_port=smtp_port,
            sender=sender,
            password=password,
            recipients=recipients,
            msg=msg
        )
        
        logger.info(f"Email sent successfully to {len(recipients)} recipient(s)")
        print(f"✅ Email sent successfully to {len(recipients)} recipient(s)")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP Authentication failed. Check credentials: {e}")
        print(f"❌ Authentication failed. Check your email credentials.")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error after retries: {e}")
        print(f"❌ Failed to send email: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending email: {e}")
        print(f"❌ Failed to send email: {e}")
        return False

if __name__ == "__main__":
    # Current date/time for the report
    current_date = datetime.now().strftime('%B %d, %Y')
    current_time = datetime.now().strftime('%I:%M %p')

    print(f"Sending interactive demo email at {current_time}...")

    # Create interactive demo content
    interactive_content = f"""
    <div class="alert info">
        📊 Interactive Report Demo - {current_date} at {current_time}
    </div>

    <h2>Performance Dashboard</h2>
    
    <div class="kpi-grid">
        <div class="kpi-card">
            <h3>Daily Revenue</h3>
            <p>$8,459</p>
        </div>
        <div class="kpi-card">
            <h3>Active Users</h3>
            <p>1,234</p>
        </div>
        <div class="kpi-card">
            <h3>Customer Satisfaction</h3>
            <p>94%</p>
        </div>
    </div>

    <div class="card-grid">
        <div class="card">
            <h3>🌟 Top Performer</h3>
            <p>Sales Team Alpha</p>
            <span class="status success">Exceeding Target</span>
        </div>
        <div class="card">
            <h3>📈 Growth Markets</h3>
            <p>APAC Region</p>
            <span class="status warning">High Potential</span>
        </div>
    </div>

    <div class="alert success">
        🎯 All KPIs are meeting or exceeding expectations
    </div>

    <h3>Monthly Trends</h3>
    <table>
        <tr>
            <th>Metric</th>
            <th>Current</th>
            <th>Previous</th>
            <th>Change</th>
        </tr>
        <tr>
            <td>Revenue</td>
            <td>$245,678</td>
            <td>$232,456</td>
            <td><span class="status success">+5.6%</span></td>
        </tr>
        <tr>
            <td>Users</td>
            <td>45,678</td>
            <td>43,234</td>
            <td><span class="status success">+5.6%</span></td>
        </tr>
    </table>

    <div style="text-align: center; margin-top: 30px;">
        <a href="https://dashboard.example.com" class="button">View Full Dashboard</a>
    </div>
    """

    # Send the interactive demo
    success = send_email(
        subject=f"Interactive Dashboard Demo - {current_date}",
        body=interactive_content
    )

    if success:
        print("✅ Interactive demo email sent successfully!")
        print("\nThis demo showed how to use:")
        print("1. KPI Cards with animations")
        print("2. Status indicators (success/warning)")
        print("3. Interactive cards with hover effects")
        print("4. Modern table design")
        print("5. Alert boxes")
        print("6. Gradient header")
        print("7. Interactive buttons")
    else:
        print("❌ Failed to send demo email")