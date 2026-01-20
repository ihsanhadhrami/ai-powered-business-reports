"""
Email Report App - Main Entry Point
Run this file to generate and send automated business reports

Usage:
    python run_report.py              # Send email with current data
    python run_report.py --dry-run    # Preview report without sending
    python run_report.py --schedule   # Run on schedule (daily at configured time)
"""

import os
import sys
import argparse
import pandas as pd
from datetime import datetime

# Import project modules
from business_metrics import BusinessMetrics
from ai_insights import generate_metric_insights, generate_email_content_from_metrics
from automated_email import send_email
from config import DATA_SOURCE, REPORT_TIME, REPORT_FREQUENCY
from utils.logger import setup_logger
from utils.validators import validate_csv_data, ValidationError

# Initialize logger
logger = setup_logger(__name__)


def load_data_from_csv(csv_path: str) -> pd.DataFrame:
    """
    Load and validate business data from CSV file.
    
    Args:
        csv_path: Path to the CSV file
    
    Returns:
        Validated DataFrame or None if error
    """
    if not os.path.exists(csv_path):
        logger.error(f"CSV file not found: {csv_path}")
        print(f"❌ Error: CSV file not found at '{csv_path}'")
        print(f"\n💡 Tip: Place your CSV file in the 'data/' folder")
        print(f"   Required columns: Date, and any of: Revenue, Sales, Customer_Count")
        return None
    
    try:
        df = pd.read_csv(csv_path)
        logger.info(f"Loaded {len(df)} rows from {csv_path}")
        
        # Validate data
        df = validate_csv_data(df, required_columns=['Date'])
        
        print(f"✅ Loaded {len(df)} rows from {csv_path}")
        
        # Show available metrics
        data_columns = [col for col in df.columns if col != 'Date']
        print(f"📊 Available metrics: {', '.join(data_columns)}")
        
        return df
    except ValidationError as e:
        logger.error(f"CSV validation failed: {e}")
        print(f"❌ Validation Error: {e}")
        return None
    except Exception as e:
        logger.error(f"Error loading CSV: {e}")
        print(f"❌ Error loading CSV: {e}")
        return None


def save_html_report(html_content: str, output_path: str) -> bool:
    """
    Save HTML report to file for preview.
    
    Args:
        html_content: HTML content to save
        output_path: Path to save the file
    
    Returns:
        True if successful, False otherwise
    """
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        logger.info(f"Report saved to: {output_path}")
        print(f"✅ Report saved to: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving report: {e}")
        print(f"❌ Error saving report: {e}")
        return False


def generate_and_send_report(dry_run: bool = False, output_path: str = None) -> bool:
    """
    Main function to generate and send business report.
    
    Args:
        dry_run: If True, save report without sending
        output_path: Path for dry-run output file
    
    Returns:
        True if successful, False otherwise
    """
    logger.info(f"Starting report generation (dry_run={dry_run})")
    
    print("=" * 70)
    print("📧 EMAIL REPORT APP - AUTOMATED BUSINESS REPORTING")
    print("=" * 70)
    print()
    
    # Step 1: Load data from CSV
    print("Step 1️⃣: Loading business data from CSV...")
    csv_path = DATA_SOURCE.get('path', 'data/sample_data.csv')
    df = load_data_from_csv(csv_path)
    
    if df is None:
        logger.error("Cannot proceed without valid data")
        print("\n❌ Cannot proceed without valid data")
        return False
    
    print(f"   Date range: {df['Date'].min()} to {df['Date'].max()}")
    print()
    
    # Step 2: Calculate business metrics
    print("Step 2️⃣: Calculating business metrics and KPIs...")
    try:
        metrics = BusinessMetrics(df)
        kpis = metrics.calculate_kpis()
        
        print("✅ Key Performance Indicators:")
        for key, value in kpis.items():
            if isinstance(value, float):
                if 'growth' in key:
                    print(f"   • {key.replace('_', ' ').title()}: {value:+.2f}%")
                else:
                    print(f"   • {key.replace('_', ' ').title()}: ${value:,.2f}" if 'revenue' in key else f"   • {key.replace('_', ' ').title()}: {value:,.2f}")
            else:
                print(f"   • {key.replace('_', ' ').title()}: {value}")
        print()
    except Exception as e:
        print(f"❌ Error calculating metrics: {e}")
        return False
    
    # Step 3: Generate AI insights
    print("Step 3️⃣: Generating AI-powered insights...")
    try:
        insights = generate_metric_insights(kpis)
        print("✅ AI Analysis Generated:")
        preview = insights[:200] + "..." if len(insights) > 200 else insights
        print(f"   {preview}")
        print()
    except Exception as e:
        print(f"⚠️  Warning: Could not generate AI insights: {e}")
        insights = "AI insights unavailable - please check AI configuration."
        print()
    
    # Step 4: Generate email content
    print("Step 4️⃣: Generating email report...")
    try:
        report_title = f"Business Performance Report - {datetime.now().strftime('%B %d, %Y')}"
        email_content = generate_email_content_from_metrics(kpis, report_title)
        
        print(f"✅ Email generated:")
        print(f"   Subject: {email_content['subject']}")
        print()
    except Exception as e:
        print(f"❌ Error generating email: {e}")
        return False
    
    # Step 5: Send or save report
    if dry_run:
        print("Step 5️⃣: Saving report (DRY RUN - No email will be sent)...")
        output_file = output_path or 'output/report.html'
        if save_html_report(email_content['body'], output_file):
            print()
            print("=" * 70)
            print("✅ DRY RUN COMPLETED SUCCESSFULLY")
            print("=" * 70)
            print(f"📄 Report saved to: {output_file}")
            print("💡 Open the HTML file in a browser to preview the email")
            return True
        return False
    else:
        print("Step 5️⃣: Sending email report...")
        try:
            success = send_email(
                subject=email_content['subject'],
                body=email_content['body']
            )
            
            if success:
                print()
                print("=" * 70)
                print("✅ EMAIL SENT SUCCESSFULLY")
                print("=" * 70)
                print(f"📧 Recipients: Check your inbox for '{email_content['subject']}'")
                return True
            else:
                print()
                print("=" * 70)
                print("❌ EMAIL SENDING FAILED")
                print("=" * 70)
                print("💡 Check your SMTP credentials in config.py")
                return False
        except Exception as e:
            print(f"❌ Error sending email: {e}")
            return False


def run_scheduled():
    """Run the report on a schedule."""
    import schedule
    import time
    
    print("=" * 70)
    print("⏰ SCHEDULED MODE - Email Report Automation")
    print("=" * 70)
    print(f"📅 Frequency: {REPORT_FREQUENCY}")
    print(f"⏰ Time: {REPORT_TIME}")
    print("Press Ctrl+C to stop")
    print("=" * 70)
    print()
    
    # Schedule the report
    if REPORT_FREQUENCY == "daily":
        schedule.every().day.at(REPORT_TIME).do(generate_and_send_report)
        print(f"✅ Scheduled daily report at {REPORT_TIME}")
    elif REPORT_FREQUENCY == "weekly":
        schedule.every().monday.at(REPORT_TIME).do(generate_and_send_report)
        print(f"✅ Scheduled weekly report (Mondays) at {REPORT_TIME}")
    elif REPORT_FREQUENCY == "monthly":
        # Run on 1st of each month
        schedule.every().day.at(REPORT_TIME).do(
            lambda: generate_and_send_report() if datetime.now().day == 1 else None
        )
        print(f"✅ Scheduled monthly report (1st of month) at {REPORT_TIME}")
    
    # Keep the scheduler running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\n\n⏹️  Scheduler stopped by user")


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="Email Report App - Automated Business Reporting",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_report.py                        # Send email now
  python run_report.py --dry-run              # Preview without sending
  python run_report.py --dry-run --output report.html
  python run_report.py --schedule             # Run on schedule
        """
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Generate report without sending email (saves to HTML file)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='output/report.html',
        help='Output path for dry-run HTML file (default: output/report.html)'
    )
    
    parser.add_argument(
        '--schedule',
        action='store_true',
        help='Run on schedule (configured in config.py)'
    )
    
    args = parser.parse_args()
    
    # Run based on mode
    if args.schedule:
        run_scheduled()
    else:
        success = generate_and_send_report(
            dry_run=args.dry_run,
            output_path=args.output
        )
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
