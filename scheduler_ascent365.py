"""
WordPress Monitor Scheduler - Ascent Innovation
================================================
Monitors: https://www.ascent365.com
Schedule: Daily at 6:00 AM
Email: prabhuofficial2003@gmail.com
"""
import os
import sys
import signal
import time
from pathlib import Path
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Global shutdown flag
shutdown_requested = False

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    global shutdown_requested
    print("\n Shutdown signal received. Stopping scheduler...")
    shutdown_requested = True

def run_scheduler():
    """Run the scheduler for Ascent365."""
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    from pytz import timezone
    from utils.logger import setup_logger
    from main import WordPressMonitor
    from utils.alerts import create_alert_manager
    from utils.config_loader import ConfigLoader
    
    # Setup logger
    logger = setup_logger("ascent365_scheduler", "logs/ascent365_scheduler.log")
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Load config
    config_path = "config/ascent365.yaml"
    config = ConfigLoader(config_path)
    
    # Get schedule time from config for display
    schedule_time = config.get('schedule', 'check_time', default='06:00')
    
    logger.info("="*60)
    logger.info("Starting Ascent365 Monitor Scheduler")
    logger.info("="*60)
    logger.info("Website: https://www.ascent365.com")
    logger.info(f"Schedule: Daily at {schedule_time} (Asia/Kolkata)")
    logger.info("Email: prabhuofficial2003@gmail.com")
    logger.info("Pages: /, /about/")
    logger.info("Press Ctrl+C to stop (works immediately!)")
    logger.info("="*60)
    
    def run_check_and_email():
        """Run monitoring check and send email report."""
        try:
            logger.info("")
            logger.info(" Starting scheduled check for Ascent365...")
            logger.info(f" Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Run the monitor
            monitor = WordPressMonitor(config_path)
            result = monitor.run_all_checks(
                generate_report=True,
                use_browser=False,
                headless=True
            )
            
            # Get report path
            report_html = result.get('report_path')
            
            if not report_html:
                logger.error(" No report generated!")
                return
            
            logger.info(f" Report generated: {report_html}")
            
            # Generate PDF
            from utils.reporting import ReportGenerator
            report_gen = ReportGenerator("reports/ascent365")
            
            pdf_path = report_gen.convert_html_to_pdf(report_html)
            
            if not pdf_path or not Path(pdf_path).exists():
                logger.error(" PDF generation failed!")
                return
            
            logger.info(f" PDF generated: {pdf_path}")
            
            # Send email with PDF
            alert_manager = create_alert_manager(config.to_dict())
            
            email_result = alert_manager.send_report_email(
                recipient_emails=["prabhuofficial2003@gmail.com"],
                pdf_path=pdf_path,
                report_summary={
                    'critical_issues': result.get('critical_issues', 0),
                    'high_issues': result.get('high_issues', 0),
                    'medium_issues': result.get('medium_issues', 0),
                    'low_issues': result.get('low_issues', 0),
                    'total_issues': result.get('total_issues', 0),
                    'avg_response_time': result.get('avg_response_time', 0),
                    'uptime_percentage': result.get('uptime_percentage', 100),
                    'pages_checked': result.get('pages_checked', 0),
                },
                website_name="Ascent Innovation",
                website_url="https://www.ascent365.com"
            )
            
            if email_result.get('status') == 'success':
                logger.info(f" Email sent successfully to prabhuofficial2003@gmail.com")
            else:
                logger.error(f" Email failed: {email_result.get('message')}")
            
            logger.info("="*60)
            logger.info(f" Check completed!")
            logger.info(f"   Issues: {result.get('total_issues', 0)} total")
            logger.info(f"   - Critical: {result.get('critical_issues', 0)}")
            logger.info(f"   - High: {result.get('high_issues', 0)}")
            logger.info(f"   - Medium: {result.get('medium_issues', 0)}")
            logger.info(f"   - Low: {result.get('low_issues', 0)}")
            logger.info("="*60)
            logger.info(" Next check: Tomorrow at 6:00 AM")
            logger.info("="*60)
            
        except Exception as e:
            logger.error(f" Check failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    # Create scheduler
    scheduler = BackgroundScheduler(
        timezone=timezone('Asia/Kolkata'),
        job_defaults={
            'coalesce': True,
            'max_instances': 1,
            'misfire_grace_time': 300
        }
    )
    
    # Get schedule time from config
    schedule_time = config.get('schedule', 'check_time', default='06:00')
    hour, minute = map(int, schedule_time.split(':'))
    
    logger.info(f"Configured schedule time: {schedule_time}")
    
    # Add job: Daily at configured time
    scheduler.add_job(
        run_check_and_email,
        trigger=CronTrigger(
            hour=hour,
            minute=minute,
            timezone='Asia/Kolkata'
        ),
        id='ascent365_daily_check',
        name=f'Ascent365 Daily Check at {schedule_time}',
        replace_existing=True
    )
    
    # Start scheduler
    global shutdown_requested
    
    try:
        scheduler.start()
        logger.info(" Scheduler started successfully!")
        logger.info(" Waiting for scheduled jobs...")
        logger.info("   Next run: Daily at 6:00 AM (Asia/Kolkata)")
        logger.info("")
        logger.info(" TIP: Press Ctrl+C anytime to stop")
        
        # Keep main thread alive
        while not shutdown_requested:
            time.sleep(1)
        
        logger.info(" Shutdown requested...")
        
    except (KeyboardInterrupt, SystemExit):
        logger.info(" Interrupt received")
        shutdown_requested = True
    
    except Exception as e:
        logger.error(f" Scheduler error: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    finally:
        if scheduler.running:
            logger.info("Stopping scheduler...")
            scheduler.shutdown(wait=False)
        logger.info(" Scheduler stopped successfully")
        logger.info("="*60)

if __name__ == "__main__":
    run_scheduler()
