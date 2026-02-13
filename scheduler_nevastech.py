"""
WordPress Monitor Scheduler - Automated scheduling of checks.
"""
import os
import sys
import signal
import threading
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Load environment variables from .env file
import load_env

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import time

from main import WordPressMonitor
from utils.config_loader import ConfigLoader
from utils.logger import setup_logger

# Global flag for graceful shutdown
shutdown_requested = False

def signal_handler(signum, frame):
    """Handle Ctrl+C and other signals gracefully."""
    global shutdown_requested
    shutdown_requested = True
    print("\n🛑 Shutdown requested... Waiting for current operation to complete.")
    print("   Press Ctrl+C again to force quit (may leave processes running).")
    
    # Second Ctrl+C forces immediate exit
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(1))


def create_scheduler(config_path: str = "config/config.yaml"):
    """Create and configure the scheduler."""
    config = ConfigLoader(config_path)
    logger = setup_logger("scheduler", "logs/scheduler.log")
    
    scheduler = BackgroundScheduler()
    
    # Get schedule configuration
    schedule_config = config.get('schedule', default={})
    check_interval = schedule_config.get('check_interval', 'daily')
    check_time = schedule_config.get('check_time', '03:00')
    timezone = schedule_config.get('timezone', 'UTC')
    
    # Parse check time
    hour, minute = map(int, check_time.split(':'))
    
    def run_check():
        """Execute a monitoring check and send PDF report to clients.
        
        Uses a headless browser (Playwright) for comprehensive checks including:
        - JavaScript execution
        - Form testing
        - Content integrity verification
        - Performance metrics
        - Screenshot capture
        
        Can be interrupted with Ctrl+C.
        """
        global shutdown_requested
        
        if shutdown_requested:
            logger.info("Check skipped due to shutdown request")
            return
        
        logger.info(f"Starting scheduled check at {datetime.now()}")
        logger.info("Running with HEADLESS BROWSER (invisible browser for comprehensive checks)")
        
        check_completed = False
        
        def run_check_with_timeout():
            """Run the actual check in a separate context."""
            nonlocal check_completed
            try:
                monitor = WordPressMonitor(config_path)
                # Always run with headless browser for comprehensive checks
                result = monitor.run_all_checks(
                    use_browser=True,   # Use headless browser for comprehensive checks
                    headless=True       # Run in headless mode (no visible windows)
                )
                logger.info(f"Check completed: {result.get('total_issues', 0)} issues found")
                
                # Get report path from result
                report_html = result.get('report_path')
                if report_html:
                    logger.info(f"Report generated: {report_html}")
                    
                    # Generate PDF from HTML report
                    from utils.reporting import ReportGenerator
                    report_gen = ReportGenerator()
                    pdf_path = report_gen.convert_html_to_pdf(report_html)
                    
                    if pdf_path:
                        logger.info(f"PDF generated: {pdf_path}")
                        
                        # Send email with PDF attachment to configured recipients
                        email_config = config.get('alerts', 'email', default={})
                        recipients = email_config.get('recipients', [])
                        
                        if recipients and email_config.get('enabled', False):
                            from utils.alerts import create_alert_manager
                            alert_mgr = create_alert_manager(config.to_dict())
                            
                            # Prepare report summary for email
                            report_summary = {
                                'critical_issues': result.get('critical_issues', 0),
                                'high_issues': result.get('high_issues', 0),
                                'medium_issues': result.get('medium_issues', 0),
                                'low_issues': result.get('low_issues', 0),
                                'total_issues': result.get('total_issues', 0),
                                'avg_response_time': result.get('avg_response_time', 0),
                                'uptime_percentage': result.get('uptime_percentage', 100),
                                'pages_checked': result.get('pages_checked', 0)
                            }
                            
                            # Send email
                            email_result = alert_mgr.send_report_email(
                                recipient_emails=recipients,
                                pdf_path=pdf_path,
                                report_summary=report_summary,
                                website_name=config.get('website', 'name', default='WordPress Site'),
                                website_url=config.get_website_url()
                            )
                            
                            if email_result.get('status') == 'success':
                                logger.info(f"Report PDF emailed successfully to: {', '.join(recipients)}")
                            else:
                                logger.warning(f"Failed to email report: {email_result.get('message')}")
                        else:
                            if not recipients:
                                logger.info("No email recipients configured in config.yaml")
                            else:
                                logger.info("Email alerts disabled in config.yaml")
                    else:
                        logger.warning("Failed to generate PDF report")
                else:
                    logger.warning("No HTML report path in results")
                
                check_completed = True
                    
            except KeyboardInterrupt:
                logger.warning("Check interrupted by user")
                raise
            except Exception as e:
                logger.error(f"Scheduled check failed: {e}")
                import traceback
                traceback.print_exc()
        
        # Execute the check
        try:
            run_check_with_timeout()
        except KeyboardInterrupt:
            logger.warning("Check interrupted - cleaning up...")
            shutdown_requested = True
            raise
        except Exception as e:
            logger.error(f"Check execution error: {e}")
    
    # Configure trigger based on interval
    if check_interval == 'hourly':
        trigger = CronTrigger(minute=minute, timezone=timezone)
    elif check_interval == 'daily':
        trigger = CronTrigger(hour=hour, minute=minute, timezone=timezone)
    elif check_interval.startswith('*/'):
        # Custom interval like */30 for every 30 minutes
        interval = int(check_interval[2:])
        trigger = CronTrigger(minute=f"*/{interval}", timezone=timezone)
    else:
        # Assume it's a cron expression
        trigger = CronTrigger.from_crontab(check_interval, timezone=timezone)
    
    scheduler.add_job(run_check, trigger, id='wordpress_monitor', replace_existing=True)
    
    logger.info(f"Scheduler configured: {check_interval} at {check_time} ({timezone})")
    
    return scheduler


def run_scheduler(config_path: str = "config/config.yaml"):
    """Run the scheduler."""
    logger = setup_logger("scheduler", "logs/scheduler.log")
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("Starting WordPress Monitor Scheduler")
    logger.info("Press Ctrl+C to stop the scheduler (works immediately!)")
    
    scheduler = create_scheduler(config_path)
    
    global shutdown_requested
    
    try:
        # Start scheduler in background
        scheduler.start()
        logger.info("Scheduler started and running...")
        logger.info("Waiting for scheduled jobs... Press Ctrl+C anytime to exit")
        
        # Keep the main thread alive with a sleep loop
        # This allows Windows to properly catch Ctrl+C
        while not shutdown_requested:
            time.sleep(1)  # Check every second
        
        logger.info("Shutdown flag detected, stopping...")
        
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutdown signal received")
        shutdown_requested = True
        
    except Exception as e:
        logger.error(f"Scheduler error: {e}")
        raise
        
    finally:
        # Ensure cleanup
        if scheduler.running:
            logger.info("Stopping scheduler...")
            scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped successfully")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='WordPress Monitor Scheduler')
    parser.add_argument('--config', '-c', default='config/config.yaml',
                       help='Path to configuration file')
    
    args = parser.parse_args()
    run_scheduler(args.config)
