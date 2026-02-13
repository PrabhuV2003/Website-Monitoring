"""
WordPress Monitor - Main Application
=====================================
Automated monitoring tool for WordPress websites.
"""
import os
import sys
import uuid
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from utils.config_loader import ConfigLoader, get_config
from utils.database import Database, get_database
from utils.alerts import AlertManager, create_alert_manager
from utils.reporting import ReportGenerator
from utils.logger import setup_logger, get_logger

from monitors.uptime_monitor import UptimeMonitor
from monitors.form_tester import FormTester
from monitors.link_checker import LinkChecker
from monitors.wordpress_checker import WordPressChecker
from monitors.performance_monitor import PerformanceMonitor
from monitors.content_checker import ContentChecker
from monitors.seo_checker import SEOChecker
from monitors.image_checker import ImageChecker
from monitors.video_checker import VideoChecker


class WordPressMonitor:
    """Main WordPress monitoring orchestrator."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the WordPress Monitor."""
        self.config_path = Path(config_path)
        if not self.config_path.is_absolute():
            self.config_path = PROJECT_ROOT / config_path
        
        self.config = ConfigLoader(str(self.config_path))
        self.base_url = self.config.get_website_url()
        
        self.logger = setup_logger(
            "wordpress_monitor",
            self.config.get('logging', 'file', default='logs/monitor.log'),
            self.config.get('logging', 'level', default='INFO')
        )
        
        self.db = get_database(self.config.to_dict())
        self.alert_manager = create_alert_manager(self.config.to_dict())
        self.report_generator = ReportGenerator(
            self.config.get('reports', 'output_dir', default='reports')
        )
        
        self.monitors = []
        self.results = []
        self.check_id = None
    
    def _initialize_monitors(self, pages: List[str] = None, use_browser: bool = False, headless: bool = True,
                             ignore_header: bool = False, ignore_footer: bool = False,
                             main_content_only: bool = False):
        """Initialize all monitor instances.
        
        Args:
            pages: Optional list of specific pages to check
            use_browser: Use Selenium browser instead of HTTP requests
            headless: Run browser in headless mode
            ignore_header: Skip links/images in header and navigation elements
            ignore_footer: Skip links/images in footer elements
            main_content_only: Only check elements in main content area
        """
        config_dict = self.config.to_dict()
        
        # Override critical_pages if custom pages are provided
        if pages:
            config_dict['critical_pages'] = pages
        
        # Add browser settings
        config_dict['use_browser'] = use_browser
        config_dict['headless'] = headless
        
        # Add content filtering settings
        config_dict['ignore_header'] = ignore_header
        config_dict['ignore_footer'] = ignore_footer
        config_dict['main_content_only'] = main_content_only
        
        # Add cancel event if available (set by dashboard stop button)
        if hasattr(self, '_cancel_event'):
            config_dict['_cancel_event'] = self._cancel_event
        
        self.monitors = [
            UptimeMonitor(config_dict, self.base_url),
            FormTester(config_dict, self.base_url),
            LinkChecker(config_dict, self.base_url),
            ImageChecker(config_dict, self.base_url),
            VideoChecker(config_dict, self.base_url),
            WordPressChecker(config_dict, self.base_url),
            PerformanceMonitor(config_dict, self.base_url),
            ContentChecker(config_dict, self.base_url),
            SEOChecker(config_dict, self.base_url),
        ]
    
    def run_all_checks(self, generate_report: bool = True, pages: List[str] = None,
                       use_browser: bool = False, headless: bool = True,
                       ignore_header: bool = False, ignore_footer: bool = False,
                       main_content_only: bool = False) -> Dict[str, Any]:
        """Run all monitoring checks.
        
        Args:
            generate_report: Whether to generate HTML report
            pages: Optional list of specific pages to check (e.g., ['/', '/about/'])
            use_browser: Use Selenium browser instead of HTTP requests
            headless: Run browser in headless mode
            ignore_header: Skip links/images in header and navigation elements
            ignore_footer: Skip links/images in footer elements
            main_content_only: Only check elements in main content area
        """
        self.check_id = f"chk_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        start_time = time.time()
        
        self.logger.info(f"Starting monitoring check: {self.check_id}")
        self.logger.info(f"Target: {self.base_url}")
        
        if pages:
            self.logger.info(f"Custom pages: {pages}")
        
        if use_browser:
            mode = "visible browser" if not headless else "headless browser"
            self.logger.info(f"Mode: {mode}")
        
        if not self.base_url or self.base_url == "https://yourwordpresssite.com":
            self.logger.error("Website URL not configured!")
            return {'error': 'Website URL not configured'}
        
        # Create check record
        self.db.create_check(self.check_id)
        
        # Initialize monitors with optional custom pages and filtering
        self._initialize_monitors(pages=pages, use_browser=use_browser, headless=headless,
                                  ignore_header=ignore_header, ignore_footer=ignore_footer,
                                  main_content_only=main_content_only)
        
        # Run all monitors sequentially
        all_results = []
        total_monitors = len(self.monitors)
        for idx, monitor in enumerate(self.monitors, 1):
            # Check for cancellation before each monitor
            if hasattr(self, '_cancel_event') and self._cancel_event.is_set():
                self.logger.warning(f"Check cancelled by user after {idx-1}/{total_monitors} monitors")
                break
            
            try:
                self.logger.info(f"")
                self.logger.info(f"{'='*50}")
                self.logger.info(f"[{idx}/{total_monitors}] Running {monitor.name.upper()} monitor...")
                self.logger.info(f"{'='*50}")
                results = monitor.run()
                all_results.extend(results)
                
                # Store results in database
                for result in results:
                    self.db.add_result(self.check_id, **result.to_dict())
                    
            except Exception as e:
                self.logger.error(f"Monitor {monitor.name} failed: {e}")
                all_results.append({
                    'monitor_type': monitor.name,
                    'status': 'error',
                    'message': f'Monitor failed: {str(e)}',
                    'severity': 'high'
                })
        
        self.results = all_results
        
        # Calculate statistics
        duration = time.time() - start_time
        stats = self._calculate_stats(duration)
        
        # Complete check record
        self.db.complete_check(self.check_id, {
            'critical': stats['critical_issues'],
            'high': stats['high_issues'],
            'medium': stats['medium_issues'],
            'low': stats['low_issues']
        })
        
        # Send alerts for critical/high issues
        self._send_alerts(stats)
        
        # Generate report
        if generate_report:
            report_path = self._generate_report(stats)
            stats['report_path'] = report_path
        
        self.logger.info(f"Check {self.check_id} completed in {duration:.2f}s")
        self.logger.info(f"Issues: {stats['total_issues']} total "
                        f"({stats['critical_issues']} critical, "
                        f"{stats['high_issues']} high, "
                        f"{stats['medium_issues']} medium, "
                        f"{stats['low_issues']} low)")
        
        return stats
    
    def run_quick_check(self) -> Dict[str, Any]:
        """Run a quick uptime and basic health check."""
        self.check_id = f"quick_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.logger.info(f"Running quick check: {self.check_id}")
        
        config_dict = self.config.to_dict()
        
        # Only run uptime monitor for quick check
        uptime_monitor = UptimeMonitor(config_dict, self.base_url)
        results = uptime_monitor.run()
        
        stats = uptime_monitor.get_stats()
        
        # Send alert if site is down
        critical_results = [r for r in results if r.severity == 'critical']
        if critical_results:
            self.alert_manager.send_downtime_alert(
                self.base_url,
                critical_results[0].message
            )
        
        return stats
    
    def run_link_check_only(self, pages: List[str] = None, limit: int = 0, 
                           generate_report: bool = True,
                           use_browser: bool = False, headless: bool = True,
                           ignore_header: bool = False, ignore_footer: bool = False,
                           main_content_only: bool = False) -> Dict[str, Any]:
        """Run link checker only (fast mode) with optional page filter and limit.
        
        Args:
            pages: List of specific pages to check (e.g., ['/', '/about/']). 
                   If None, uses critical_pages from config.
            limit: Max links to check per page (0 = unlimited)
            generate_report: Whether to generate HTML report
            use_browser: If True, use Selenium browser instead of HTTP requests
            headless: If True, run browser in headless mode (invisible)
            ignore_header: Skip links in header and navigation elements
            ignore_footer: Skip links in footer elements
            main_content_only: Only check links in main content area
        """
        self.check_id = f"fast_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        start_time = time.time()
        
        self.logger.info(f"Starting FAST link check: {self.check_id}")
        self.logger.info(f"Target: {self.base_url}")
        
        if use_browser:
            mode = "visible browser" if not headless else "headless browser"
            self.logger.info(f"Mode: {mode}")
        else:
            self.logger.info(f"Mode: HTTP requests (fast)")
        
        if not self.base_url or self.base_url == "https://yourwordpresssite.com":
            self.logger.error("Website URL not configured!")
            return {'error': 'Website URL not configured'}
        
        # Create check record
        self.db.create_check(self.check_id)
        
        # Create modified config with custom pages if provided
        config_dict = self.config.to_dict()
        if pages:
            config_dict['critical_pages'] = pages
            self.logger.info(f"Custom pages: {pages}")
        
        # Set link limit if provided
        if limit > 0:
            if 'link_checker' not in config_dict:
                config_dict['link_checker'] = {}
            config_dict['link_checker']['max_links_per_page'] = limit
            self.logger.info(f"Link limit per page: {limit}")
        
        # Set browser mode
        config_dict['use_browser'] = use_browser
        config_dict['headless'] = headless
        
        # Set content filtering options
        config_dict['ignore_header'] = ignore_header
        config_dict['ignore_footer'] = ignore_footer
        config_dict['main_content_only'] = main_content_only
        
        # Add cancel event if available
        if hasattr(self, '_cancel_event'):
            config_dict['_cancel_event'] = self._cancel_event
        
        # Only run the link checker
        from monitors.link_checker import LinkChecker
        link_checker = LinkChecker(config_dict, self.base_url)
        
        # Apply limit if set
        if limit > 0:
            link_checker.max_links_per_page = limit
        
        all_results = []
        try:
            self.logger.info("Running link checker...")
            results = link_checker.run()
            all_results.extend(results)
            
            # Store results in database
            for result in results:
                self.db.add_result(self.check_id, **result.to_dict())
                
        except Exception as e:
            self.logger.error(f"Link checker failed: {e}")
            all_results.append({
                'monitor_type': 'links',
                'status': 'error',
                'message': f'Link checker failed: {str(e)}',
                'severity': 'high'
            })
        
        self.results = all_results
        
        # Calculate statistics
        duration = time.time() - start_time
        stats = self._calculate_stats(duration)
        stats['mode'] = 'fast'
        stats['pages_specified'] = pages if pages else 'all critical pages'
        stats['link_limit'] = limit if limit > 0 else 'unlimited'
        stats['browser_mode'] = 'browser' if use_browser else 'http'
        
        # Complete check record
        self.db.complete_check(self.check_id, {
            'critical': stats['critical_issues'],
            'high': stats['high_issues'],
            'medium': stats['medium_issues'],
            'low': stats['low_issues']
        })
        
        # Generate report
        if generate_report:
            report_path = self._generate_report(stats)
            stats['report_path'] = report_path
        
        self.logger.info(f"FAST check {self.check_id} completed in {duration:.2f}s")
        
        return stats
    
    def run_image_check_only(self, pages: List[str] = None, limit: int = 0,
                            generate_report: bool = True,
                            use_browser: bool = False, headless: bool = True,
                            ignore_header: bool = False, ignore_footer: bool = False,
                            main_content_only: bool = False) -> Dict[str, Any]:
        """Run image checker only with optional page filter and limit.
        
        Args:
            pages: List of specific pages to check (e.g., ['/', '/about/']). 
                   If None, uses critical_pages from config.
            limit: Max images to check per page (0 = unlimited)
            generate_report: Whether to generate HTML report
            use_browser: If True, use Selenium browser instead of HTTP requests
            headless: If True, run browser in headless mode (invisible)
            ignore_header: Skip images in header and navigation elements
            ignore_footer: Skip images in footer elements
            main_content_only: Only check images in main content area
        """
        self.check_id = f"img_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        start_time = time.time()
        
        self.logger.info(f"Starting IMAGE check: {self.check_id}")
        self.logger.info(f"Target: {self.base_url}")
        
        if use_browser:
            mode = "visible browser" if not headless else "headless browser"
            self.logger.info(f"Mode: {mode}")
        else:
            self.logger.info(f"Mode: HTTP requests (fast)")
        
        if not self.base_url or self.base_url == "https://yourwordpresssite.com":
            self.logger.error("Website URL not configured!")
            return {'error': 'Website URL not configured'}
        
        # Create check record
        self.db.create_check(self.check_id)
        
        # Create modified config with custom pages if provided
        config_dict = self.config.to_dict()
        if pages:
            config_dict['critical_pages'] = pages
            self.logger.info(f"Custom pages: {pages}")
        
        # Set image limit if provided
        if limit > 0:
            if 'image_checker' not in config_dict:
                config_dict['image_checker'] = {}
            config_dict['image_checker']['max_images_per_page'] = limit
            self.logger.info(f"Image limit per page: {limit}")
        
        # Set browser mode
        config_dict['use_browser'] = use_browser
        config_dict['headless'] = headless
        
        # Set content filtering options
        config_dict['ignore_header'] = ignore_header
        config_dict['ignore_footer'] = ignore_footer
        config_dict['main_content_only'] = main_content_only
        
        # Add cancel event if available
        if hasattr(self, '_cancel_event'):
            config_dict['_cancel_event'] = self._cancel_event
        
        # Only run the image checker
        image_checker = ImageChecker(config_dict, self.base_url)
        
        # Apply limit if set
        if limit > 0:
            image_checker.max_images_per_page = limit
        
        all_results = []
        try:
            self.logger.info("Running image checker...")
            results = image_checker.run()
            all_results.extend(results)
            
            # Store results in database
            for result in results:
                self.db.add_result(self.check_id, **result.to_dict())
                
        except Exception as e:
            self.logger.error(f"Image checker failed: {e}")
            import traceback
            traceback.print_exc()
            all_results.append({
                'monitor_type': 'images',
                'status': 'error',
                'message': f'Image checker failed: {str(e)}',
                'severity': 'high'
            })
        
        self.results = all_results
        
        # Calculate statistics
        duration = time.time() - start_time
        stats = self._calculate_stats(duration)
        stats['mode'] = 'images'
        stats['pages_specified'] = pages if pages else 'all critical pages'
        stats['image_limit'] = limit if limit > 0 else 'unlimited'
        stats['browser_mode'] = 'browser' if use_browser else 'http'
        stats['images_checked'] = len(image_checker.checked_images) if hasattr(image_checker, 'checked_images') else 0
        stats['broken_images'] = len(image_checker.broken_images) if hasattr(image_checker, 'broken_images') else 0
        stats['slow_images'] = len(image_checker.slow_images) if hasattr(image_checker, 'slow_images') else 0
        stats['missing_alt'] = len(image_checker.missing_alt_images) if hasattr(image_checker, 'missing_alt_images') else 0
        
        # Complete check record
        self.db.complete_check(self.check_id, {
            'critical': stats['critical_issues'],
            'high': stats['high_issues'],
            'medium': stats['medium_issues'],
            'low': stats['low_issues']
        })
        
        # Generate report
        if generate_report:
            report_path = self._generate_report(stats)
            stats['report_path'] = report_path
        
        self.logger.info(f"IMAGE check {self.check_id} completed in {duration:.2f}s")
        
        return stats

    
    def run_video_check_only(self, pages: List[str] = None,
                             generate_report: bool = True,
                             use_browser: bool = False, headless: bool = True) -> Dict[str, Any]:
        """Run only video checking (YouTube, Vimeo, HTML5 videos).
        
        Args:
            pages: List of pages to check (e.g., ['/', '/about/'])
            generate_report: Whether to generate HTML report
            use_browser: Use Selenium browser instead of HTTP requests
            headless: Run browser in headless mode (invisible)
        
        Returns:
            Dictionary with check statistics
        """
        self.check_id = f"vid_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        start_time = time.time()
        
        mode = "visible browser" if (use_browser and not headless) else ("headless browser" if use_browser else "HTTP requests")
        self.logger.info(f"Starting VIDEO check: {self.check_id}")
        self.logger.info(f"Target: {self.base_url}")
        self.logger.info(f"Mode: {mode}")
        
        if not self.base_url or self.base_url == "https://yourwordpresssite.com":
            self.logger.error("Website URL not configured!")
            return {'error': 'Website URL not configured'}
        
        # Create check record
        self.db.create_check(self.check_id)
        
        # Use specified pages or fall back to critical pages
        if pages:
            self.logger.info(f"Custom pages: {pages}")
        
        # Build config for video checker
        config_dict = self.config.to_dict()
        if pages:
            config_dict['critical_pages'] = pages
        config_dict['use_browser'] = use_browser
        config_dict['headless'] = headless
        
        # Create video checker
        self.logger.info("Running video checker...")
        video_checker = VideoChecker(config_dict, self.base_url)
        
        all_results = []
        try:
            results = video_checker.run()
            all_results.extend(results)
            
            # Log each result
            for result in results:
                level = 'error' if result.status == 'error' else 'warning' if result.status == 'warning' else 'info'
                getattr(self.logger, level)(f"[videos] {result.message}")
        except Exception as e:
            self.logger.error(f"Video checker failed: {e}")
            import traceback
            traceback.print_exc()
            all_results.append({
                'status': 'error',
                'message': f'Video check failed: {str(e)}',
                'severity': 'high'
            })
        
        self.results = all_results
        
        # Calculate statistics
        duration = time.time() - start_time
        stats = self._calculate_stats(duration)
        stats['mode'] = 'videos'
        stats['pages_specified'] = pages if pages else 'all critical pages'
        stats['browser_mode'] = 'browser' if use_browser else 'http'
        stats['videos_checked'] = len(video_checker.checked_videos) if hasattr(video_checker, 'checked_videos') else 0
        stats['broken_videos'] = len(video_checker.broken_videos) if hasattr(video_checker, 'broken_videos') else 0
        
        # Complete check record
        self.db.complete_check(self.check_id, {
            'critical': stats['critical_issues'],
            'high': stats['high_issues'],
            'medium': stats['medium_issues'],
            'low': stats['low_issues']
        })
        
        # Generate report
        if generate_report:
            report_path = self._generate_report(stats)
            stats['report_path'] = report_path
        
        self.logger.info(f"VIDEO check {self.check_id} completed in {duration:.2f}s")
        
        return stats

    
    def _calculate_stats(self, duration: float) -> Dict[str, Any]:
        """Calculate statistics from results."""
        issues = {
            'critical': 0, 'high': 0, 'medium': 0, 'low': 0
        }
        
        for result in self.results:
            if hasattr(result, 'severity'):
                severity = result.severity
            elif isinstance(result, dict):
                severity = result.get('severity', 'low')
            else:
                severity = 'low'
            
            if hasattr(result, 'status'):
                status = result.status
            elif isinstance(result, dict):
                status = result.get('status', '')
            else:
                status = ''
            
            if status != 'success':
                if severity in issues:
                    issues[severity] += 1
        
        # Calculate average response time
        response_times = []
        for result in self.results:
            rt = None
            if hasattr(result, 'response_time'):
                rt = result.response_time
            elif isinstance(result, dict):
                rt = result.get('response_time')
            if rt:
                response_times.append(rt)
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        return {
            'check_id': self.check_id,
            'website_url': self.base_url,
            'website_name': self.config.get('website', 'name', default='WordPress Site'),
            'start_time': datetime.now().isoformat(),
            'end_time': datetime.now().isoformat(),
            'duration': duration,
            'total_checks': len(self.results),
            'total_issues': sum(issues.values()),
            'critical_issues': issues['critical'],
            'high_issues': issues['high'],
            'medium_issues': issues['medium'],
            'low_issues': issues['low'],
            'avg_response_time': round(avg_response_time, 2),
            'uptime_percentage': self.db.get_uptime_percentage(self.base_url),
            'pages_checked': len(self.config.get_critical_pages()),
            'links_checked': len([r for r in self.results if hasattr(r, 'monitor_type') and r.monitor_type == 'links']),
            'forms_tested': len(self.config.get_forms_config())
        }
    
    def _send_alerts(self, stats: Dict[str, Any]):
        """Send alerts based on check results."""
        # DISABLED: Alert emails with subject "[HIGH] WordPress Monitor Alert - X Issues Found"
        # Only report emails are sent now
        # 
        # if stats['critical_issues'] > 0 or stats['high_issues'] > 0:
        #     issues = []
        #     for result in self.results:
        #         severity = getattr(result, 'severity', None) or (result.get('severity') if isinstance(result, dict) else None)
        #         if severity in ['critical', 'high']:
        #             issues.append({
        #                 'severity': severity,
        #                 'message': getattr(result, 'message', '') or (result.get('message') if isinstance(result, dict) else ''),
        #                 'monitor': getattr(result, 'monitor_type', '') or (result.get('monitor_type') if isinstance(result, dict) else ''),
        #                 'url': getattr(result, 'url', '') or (result.get('url') if isinstance(result, dict) else '')
        #             })
        #     
        #     self.alert_manager.send_alert(
        #         f"WordPress Monitor Alert - {stats['total_issues']} Issues Found",
        #         f"Critical: {stats['critical_issues']}, High: {stats['high_issues']}",
        #         'critical' if stats['critical_issues'] > 0 else 'high',
        #         details=stats,
        #         check_id=self.check_id
        #     )
        pass  # Alert emails disabled - only report emails are sent
    
    def _generate_report(self, stats: Dict[str, Any]) -> Optional[str]:
        """Generate monitoring report."""
        issues = []
        for result in self.results:
            status = getattr(result, 'status', None) or (result.get('status') if isinstance(result, dict) else '')
            if status != 'success':
                # Get details which may contain broken_links, slow_links, etc.
                details = getattr(result, 'details', None) or (result.get('details') if isinstance(result, dict) else None)
                
                issue = {
                    'severity': getattr(result, 'severity', 'low') or (result.get('severity', 'low') if isinstance(result, dict) else 'low'),
                    'message': getattr(result, 'message', '') or (result.get('message', '') if isinstance(result, dict) else ''),
                    'monitor': getattr(result, 'monitor_type', '') or (result.get('monitor_type', '') if isinstance(result, dict) else ''),
                    'url': getattr(result, 'url', '') or (result.get('url', '') if isinstance(result, dict) else ''),
                    'details': details if details else {}
                }
                issues.append(issue)
        
        report_data = {
            'stats': stats,
            'issues': sorted(issues, key=lambda x: {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}.get(x.get('severity', 'low'), 4))
        }
        
        return self.report_generator.generate_report(
            self.check_id,
            report_data,
            self.config.get('reports', 'format', default='html')
        )


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='WordPress Monitor')
    parser.add_argument('--config', '-c', default='config/config.yaml',
                       help='Path to configuration file')
    parser.add_argument('--quick', '-q', action='store_true',
                       help='Run quick uptime check only')
    parser.add_argument('--no-report', action='store_true',
                       help='Skip report generation')
    parser.add_argument('--url', '-u', help='Override website URL')
    
    args = parser.parse_args()
    
    # Set URL from argument if provided
    if args.url:
        os.environ['WP_MONITOR_URL'] = args.url
    
    monitor = WordPressMonitor(args.config)
    
    if args.quick:
        result = monitor.run_quick_check()
    else:
        result = monitor.run_all_checks(generate_report=not args.no_report)
    
    # Exit with error code if critical issues found
    if result.get('critical_issues', 0) > 0:
        sys.exit(1)
    
    sys.exit(0)


if __name__ == '__main__':
    main()
