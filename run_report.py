"""
Email Report App - Main Entry Point
Run this file to generate and send automated business reports.

Usage:
    python run_report.py              # Send email with current data
    python run_report.py --dry-run    # Preview report without sending
    python run_report.py --schedule   # Run on schedule
"""

import argparse
import os
import sys
from datetime import datetime

import pandas as pd

from ai_insights import generate_email_content_from_metrics, generate_metric_insights
from automated_email import send_email
from business_metrics import BusinessMetrics
from config import DATA_SOURCE, REPORT_FREQUENCY, REPORT_TIME
from utils.logger import setup_logger
from utils.validators import ValidationError, validate_csv_data

logger = setup_logger(__name__)


def load_data_from_csv(csv_path: str) -> pd.DataFrame | None:
    """Load and validate business data from a CSV file."""
    if not os.path.exists(csv_path):
        logger.error("CSV file not found: %s", csv_path)
        print(f"[ERROR] CSV file not found at '{csv_path}'")
        print("\nTip: Place your CSV file in the 'data/' folder")
        print("   Required columns: Date, and any of: Revenue, Sales, Customer_Count")
        return None

    try:
        df = pd.read_csv(csv_path)
        logger.info("Loaded %s rows from %s", len(df), csv_path)

        df = validate_csv_data(df, required_columns=["Date"])

        print(f"[OK] Loaded {len(df)} rows from {csv_path}")
        data_columns = [col for col in df.columns if col != "Date"]
        print(f"Available metrics: {', '.join(data_columns)}")

        return df
    except ValidationError as e:
        logger.error("CSV validation failed: %s", e)
        print(f"[ERROR] Validation Error: {e}")
        return None
    except Exception as e:
        logger.error("Error loading CSV: %s", e)
        print(f"[ERROR] Error loading CSV: {e}")
        return None


def save_html_report(html_content: str, output_path: str) -> bool:
    """Save an HTML report to disk for preview."""
    try:
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info("Report saved to: %s", output_path)
        print(f"[OK] Report saved to: {output_path}")
        return True
    except Exception as e:
        logger.error("Error saving report: %s", e)
        print(f"[ERROR] Error saving report: {e}")
        return False


def _print_kpis(kpis: dict) -> None:
    print("[OK] Key Performance Indicators:")
    for key, value in kpis.items():
        label = key.replace("_", " ").title()
        if isinstance(value, float):
            if "growth" in key:
                print(f"   - {label}: {value:+.2f}%")
            elif "revenue" in key:
                print(f"   - {label}: ${value:,.2f}")
            else:
                print(f"   - {label}: {value:,.2f}")
        else:
            print(f"   - {label}: {value}")


def generate_and_send_report(dry_run: bool = False, output_path: str | None = None) -> bool:
    """Generate a business report and either save it or send it by email."""
    logger.info("Starting report generation (dry_run=%s)", dry_run)

    print("=" * 70)
    print("EMAIL REPORT APP - AUTOMATED BUSINESS REPORTING")
    print("=" * 70)
    print()

    print("Step 1: Loading business data from CSV...")
    csv_path = DATA_SOURCE.get("path", "data/sample_data.csv")
    df = load_data_from_csv(csv_path)

    if df is None:
        logger.error("Cannot proceed without valid data")
        print("\n[ERROR] Cannot proceed without valid data")
        return False

    print(f"   Date range: {df['Date'].min()} to {df['Date'].max()}")
    print()

    print("Step 2: Calculating business metrics and KPIs...")
    try:
        metrics = BusinessMetrics(df)
        kpis = metrics.calculate_kpis()
        _print_kpis(kpis)
        print()
    except Exception as e:
        print(f"[ERROR] Error calculating metrics: {e}")
        return False

    print("Step 3: Generating report insights...")
    try:
        insights = generate_metric_insights(kpis)
        print("[OK] Insights generated:")
        preview = insights[:200] + "..." if len(insights) > 200 else insights
        print(f"   {preview}")
        print()
    except Exception as e:
        print(f"[WARN] Could not generate insights: {e}")
        insights = "Insights unavailable. Please check AI configuration."
        print()

    print("Step 4: Generating email report...")
    try:
        report_title = f"Business Performance Report - {datetime.now().strftime('%B %d, %Y')}"
        email_content = generate_email_content_from_metrics(
            kpis,
            report_title,
            insights=insights,
        )

        print("[OK] Email generated:")
        print(f"   Subject: {email_content['subject']}")
        print()
    except Exception as e:
        print(f"[ERROR] Error generating email: {e}")
        return False

    if dry_run:
        print("Step 5: Saving report (DRY RUN - no email will be sent)...")
        output_file = output_path or "output/report.html"
        if save_html_report(email_content["body"], output_file):
            print()
            print("=" * 70)
            print("[OK] DRY RUN COMPLETED SUCCESSFULLY")
            print("=" * 70)
            print(f"Report saved to: {output_file}")
            print("Open the HTML file in a browser to preview the email")
            return True
        return False

    print("Step 5: Sending email report...")
    try:
        success = send_email(
            subject=email_content["subject"],
            body=email_content["body"],
        )

        if success:
            print()
            print("=" * 70)
            print("[OK] EMAIL SENT SUCCESSFULLY")
            print("=" * 70)
            print(f"Recipients: Check your inbox for '{email_content['subject']}'")
            return True

        print()
        print("=" * 70)
        print("[ERROR] EMAIL SENDING FAILED")
        print("=" * 70)
        print("Check your SMTP credentials in .env")
        return False
    except Exception as e:
        print(f"[ERROR] Error sending email: {e}")
        return False


def run_scheduled() -> None:
    """Run the report on a schedule."""
    import schedule
    import time

    print("=" * 70)
    print("SCHEDULED MODE - Email Report Automation")
    print("=" * 70)
    print(f"Frequency: {REPORT_FREQUENCY}")
    print(f"Time: {REPORT_TIME}")
    print("Press Ctrl+C to stop")
    print("=" * 70)
    print()

    if REPORT_FREQUENCY == "daily":
        schedule.every().day.at(REPORT_TIME).do(generate_and_send_report)
        print(f"[OK] Scheduled daily report at {REPORT_TIME}")
    elif REPORT_FREQUENCY == "weekly":
        schedule.every().monday.at(REPORT_TIME).do(generate_and_send_report)
        print(f"[OK] Scheduled weekly report (Mondays) at {REPORT_TIME}")
    elif REPORT_FREQUENCY == "monthly":
        schedule.every().day.at(REPORT_TIME).do(
            lambda: generate_and_send_report() if datetime.now().day == 1 else None
        )
        print(f"[OK] Scheduled monthly report (1st of month) at {REPORT_TIME}")
    else:
        print(f"[ERROR] Invalid REPORT_FREQUENCY: {REPORT_FREQUENCY}")
        print("Use one of: daily, weekly, monthly")
        return

    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n\nScheduler stopped by user")


def main() -> None:
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
        """,
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate report without sending email (saves to HTML file)",
    )

    parser.add_argument(
        "--output",
        type=str,
        default="output/report.html",
        help="Output path for dry-run HTML file (default: output/report.html)",
    )

    parser.add_argument(
        "--schedule",
        action="store_true",
        help="Run on schedule (configured in config.py)",
    )

    args = parser.parse_args()

    if args.schedule:
        run_scheduled()
    else:
        success = generate_and_send_report(
            dry_run=args.dry_run,
            output_path=args.output,
        )
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
