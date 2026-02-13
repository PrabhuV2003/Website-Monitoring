"""
WordPress Monitor Dashboard - Enhanced Flask web interface with full feature support.
Includes: Website URL editing, real-time logs, image checking, browser mode, and more.
"""
import os
import sys
import queue
import logging
from pathlib import Path
from datetime import datetime, timedelta
import threading
import json

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from flask import Flask, render_template, jsonify, request, redirect, url_for, send_from_directory
from flask_socketio import SocketIO, emit

from utils.config_loader import ConfigLoader
from utils.database import get_database
from utils.reporting import ReportGenerator
from utils.alerts import create_alert_manager
from main import WordPressMonitor


# Custom log handler that broadcasts logs via SocketIO
class SocketIOLogHandler(logging.Handler):
    """Custom log handler that sends logs to connected clients via SocketIO."""
    
    def __init__(self, socketio):
        super().__init__()
        self.socketio = socketio
        self.setLevel(logging.INFO)
        self.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', datefmt='%H:%M:%S'))
    
    def emit(self, record):
        try:
            log_entry = self.format(record)
            self.socketio.emit('log_message', {
                'message': log_entry,
                'level': record.levelname,
                'timestamp': datetime.now().strftime('%H:%M:%S')
            })
        except Exception:
            pass


def create_app(config_path: str = "config/config.yaml"):
    """Create and configure the Flask application."""
    app = Flask(__name__,
                template_folder=str(PROJECT_ROOT / 'dashboard' / 'templates'),
                static_folder=str(PROJECT_ROOT / 'dashboard' / 'static'))
    
    config = ConfigLoader(config_path)
    app.secret_key = config.get('dashboard', 'secret_key', default='dev-secret-key-change-in-production')
    
    db = get_database(config.to_dict())
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    
    # Store config_path for later use
    app.config['MONITOR_CONFIG_PATH'] = config_path
    app.config['CONFIG_OBJECT'] = config
    
    # Set up log handler for real-time logs
    log_handler = SocketIOLogHandler(socketio)
    
    # Current check state
    check_state = {
        'running': False,
        'current_check_id': None,
        'logs': [],
        'cancel_event': threading.Event(),
        'thread': None
    }
    
    @app.route('/')
    def index():
        """Dashboard home page."""
        recent_checks = db.get_recent_checks(10)
        uptime = db.get_uptime_percentage(config.get_website_url(), days=30)
        
        return render_template('index.html',
            website_url=config.get_website_url(),
            website_name=config.get('website', 'name', default='WordPress Site'),
            critical_pages=config.get_critical_pages(),
            recent_checks=recent_checks,
            uptime_percentage=round(uptime, 2) if uptime else 100.0,
            total_checks=len(recent_checks) if recent_checks else 0
        )
    
    @app.route('/api/status')
    def api_status():
        """Get current status."""
        recent = db.get_recent_checks(1)
        if recent:
            check = recent[0]
            return jsonify({
                'status': 'ok' if check.critical_issues == 0 and check.high_issues == 0 else 'issues',
                'last_check': check.start_time.isoformat() if check.start_time else None,
                'issues': {
                    'critical': check.critical_issues or 0,
                    'high': check.high_issues or 0,
                    'medium': check.medium_issues or 0,
                    'low': check.low_issues or 0
                },
                'is_running': check_state['running']
            })
        return jsonify({
            'status': 'no_data', 
            'issues': {'critical': 0, 'high': 0, 'medium': 0, 'low': 0},
            'is_running': check_state['running']
        })
    
    @app.route('/api/checks')
    def api_checks():
        """Get recent checks."""
        limit = request.args.get('limit', 10, type=int)
        checks = db.get_recent_checks(limit)
        return jsonify([{
            'id': c.check_id,
            'start_time': c.start_time.isoformat() if c.start_time else None,
            'status': c.status,
            'critical': c.critical_issues or 0,
            'high': c.high_issues or 0,
            'medium': c.medium_issues or 0,
            'low': c.low_issues or 0,
            'total': (c.critical_issues or 0) + (c.high_issues or 0) + (c.medium_issues or 0) + (c.low_issues or 0)
        } for c in checks])
    
    @app.route('/api/uptime')
    def api_uptime():
        """Get uptime history."""
        days = request.args.get('days', 30, type=int)
        url = config.get_website_url()
        history = db.get_uptime_history(url, days)
        
        return jsonify([{
            'timestamp': h.timestamp.isoformat(),
            'is_up': h.is_up,
            'response_time': h.response_time,
            'status_code': h.status_code
        } for h in history[-100:]])
    
    @app.route('/api/performance')
    def api_performance():
        """Get performance trends."""
        days = request.args.get('days', 7, type=int)
        url = config.get_website_url()
        metrics = db.get_performance_trends(url, days)
        
        return jsonify([{
            'timestamp': m.timestamp.isoformat(),
            'ttfb': m.ttfb,
            'page_load_time': m.page_load_time,
            'pagespeed_score': m.pagespeed_score
        } for m in metrics])
    
    @app.route('/api/links/broken')
    def api_broken_links():
        """Get broken links."""
        limit = request.args.get('limit', 50, type=int)
        links = db.get_broken_links(limit)
        
        return jsonify([{
            'source': l.source_url,
            'target': l.target_url,
            'text': getattr(l, 'link_text', None) or '-',
            'status': l.status_code or l.error_type,
            'status_message': getattr(l, 'status_message', None) or '-',
            'times_detected': l.times_detected,
            'last_detected': l.last_detected.isoformat() if l.last_detected else None
        } for l in links])
    
    @app.route('/api/config', methods=['GET'])
    def api_get_config():
        """Get current configuration."""
        return jsonify({
            'website_url': config.get_website_url(),
            'website_name': config.get('website', 'name', default='WordPress Site'),
            'critical_pages': config.get_critical_pages(),
            'link_checker': config.get('link_checker', default={}),
            'image_checker': config.get('image_checker', default={}),
            'thresholds': config.get('thresholds', default={})
        })
    
    @app.route('/api/config/url', methods=['POST'])
    def api_update_url():
        """Update website URL temporarily for this session."""
        try:
            data = request.json or {}
            new_url = data.get('url', '').strip()
        
            if not new_url:
                return jsonify({'status': 'error', 'message': 'URL is required'}), 400
            
            # Ensure URL has protocol
            if not new_url.startswith(('http://', 'https://')):
                new_url = 'https://' + new_url
            
            # Set environment variable for override
            os.environ['WP_MONITOR_URL'] = new_url
            
            return jsonify({
                'status': 'success',
                'url': new_url,
                'message': f'URL updated to {new_url}'
            })
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    @app.route('/api/check/run', methods=['POST'])
    def api_run_check():
        """Trigger a manual check with options."""
        if check_state['running']:
            return jsonify({'status': 'error', 'message': 'A check is already running'}), 400
        
        try:
            data = request.json or {}
            mode = data.get('mode', 'quick')
            pages = data.get('pages', '')
            limit = data.get('limit', 0)
            use_browser = data.get('use_browser', False)
            headless = data.get('headless', True)
            generate_report = data.get('generate_report', True)
            custom_url = data.get('url', '')
            ignore_header = data.get('ignore_header', False)
            ignore_footer = data.get('ignore_footer', False)
            main_content_only = data.get('main_content_only', False)
            
            # Update URL if provided
            if custom_url:
                if not custom_url.startswith(('http://', 'https://')):
                    custom_url = 'https://' + custom_url
                os.environ['WP_MONITOR_URL'] = custom_url
            
            check_state['running'] = True
            check_state['logs'] = []
            # Reset the cancel event for a new check
            check_state['cancel_event'] = threading.Event()
            cancel_event = check_state['cancel_event']
            
            def run_check_thread():
                try:
                    # Create monitor with log handler
                    monitor = WordPressMonitor(app.config['MONITOR_CONFIG_PATH'])
                    
                    # Store cancel event on the monitor so it can pass it to sub-monitors
                    monitor._cancel_event = cancel_event
                    
                    # Add socketio log handler
                    monitor.logger.addHandler(log_handler)
                    
                    socketio.emit('check_progress', {
                        'stage': 'starting',
                        'message': f'Starting {mode} check...',
                        'mode': mode
                    })
                    
                    pages_list = [p.strip() for p in pages.split(',')] if pages else None
                    
                    if mode == 'quick':
                        result = monitor.run_quick_check()
                    elif mode == 'fast':
                        result = monitor.run_link_check_only(
                            pages=pages_list,
                            limit=int(limit) if limit else 0,
                            generate_report=generate_report,
                            use_browser=use_browser,
                            headless=headless,
                            ignore_header=ignore_header,
                            ignore_footer=ignore_footer,
                            main_content_only=main_content_only
                        )
                    elif mode == 'images':
                        result = monitor.run_image_check_only(
                            pages=pages_list,
                            limit=int(limit) if limit else 0,
                            generate_report=generate_report,
                            use_browser=use_browser,
                            headless=headless,
                            ignore_header=ignore_header,
                            ignore_footer=ignore_footer,
                            main_content_only=main_content_only
                        )
                    elif mode == 'videos':
                        result = monitor.run_video_check_only(
                            pages=pages_list,
                            generate_report=generate_report,
                            use_browser=use_browser,
                            headless=headless
                        )
                    else:
                        # Full mode - pass custom pages if specified
                        result = monitor.run_all_checks(
                            generate_report=generate_report,
                            pages=pages_list,
                            use_browser=use_browser,
                            headless=headless,
                            ignore_header=ignore_header,
                            ignore_footer=ignore_footer,
                            main_content_only=main_content_only
                        )
                    
                    # Remove log handler
                    monitor.logger.removeHandler(log_handler)
                    
                    check_state['running'] = False
                    
                    if cancel_event.is_set():
                        socketio.emit('check_complete', {
                            'stopped': True,
                            'message': 'Check was stopped by user',
                            'total_issues': result.get('total_issues', 0) if isinstance(result, dict) else 0
                        })
                    else:
                        socketio.emit('check_complete', result)
                    
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    check_state['running'] = False
                    socketio.emit('check_error', {'error': str(e)})
            
            thread = threading.Thread(target=run_check_thread)
            thread.daemon = True
            thread.start()
            check_state['thread'] = thread
            
            return jsonify({
                'status': 'started',
                'mode': mode,
                'message': f'{mode.title()} check started'
            })
            
        except Exception as e:
            check_state['running'] = False
            import traceback
            traceback.print_exc()
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    @app.route('/api/check/stop', methods=['POST'])
    def api_stop_check():
        """Stop running check by setting the cancel event."""
        if not check_state['running']:
            return jsonify({'status': 'error', 'message': 'No check is currently running'}), 400
        
        # Set the cancel event - monitors will check this and exit their loops
        check_state['cancel_event'].set()
        check_state['running'] = False
        return jsonify({'status': 'stopped', 'message': 'Check stop requested'})
    
    @app.route('/reports/<path:filename>')
    def serve_report(filename):
        """Serve generated reports."""
        reports_dir = PROJECT_ROOT / 'reports'
        return send_from_directory(str(reports_dir), filename)
    
    @app.route('/api/reports')
    def api_reports():
        """List available reports with details."""
        reports_dir = PROJECT_ROOT / 'reports'
        reports = []
        
        if reports_dir.exists():
            for file in sorted(reports_dir.glob('*.html'), key=lambda x: x.stat().st_mtime, reverse=True)[:50]:
                # Parse filename for metadata
                # Format: report_{mode}_{date}_{time}_{id}_{timestamp}.html
                parts = file.stem.split('_')
                mode = parts[1] if len(parts) > 1 else 'unknown'
                
                reports.append({
                    'filename': file.name,
                    'mode': mode,
                    'created': datetime.fromtimestamp(file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                    'created_iso': datetime.fromtimestamp(file.stat().st_mtime).isoformat(),
                    'size': file.stat().st_size,
                    'size_kb': round(file.stat().st_size / 1024, 1)
                })
        
        return jsonify(reports)
    
    @app.route('/api/reports/<filename>', methods=['DELETE'])
    def api_delete_report(filename):
        """Delete a report file."""
        try:
            reports_dir = PROJECT_ROOT / 'reports'
            file_path = reports_dir / filename
            if file_path.exists() and file_path.is_file():
                file_path.unlink()
                return jsonify({'status': 'success', 'message': f'Deleted {filename}'})
            return jsonify({'status': 'error', 'message': 'File not found'}), 404
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    @app.route('/api/reports/<filename>/pdf', methods=['POST'])
    def api_generate_pdf(filename):
        """Generate PDF from an existing HTML report."""
        try:
            reports_dir = PROJECT_ROOT / 'reports'
            html_path = reports_dir / filename
            
            if not html_path.exists():
                return jsonify({'status': 'error', 'message': 'Report not found'}), 404
            
            report_gen = ReportGenerator(output_dir=str(reports_dir))
            pdf_path = report_gen.convert_html_to_pdf(str(html_path))
            
            if pdf_path:
                pdf_filename = Path(pdf_path).name
                return jsonify({
                    'status': 'success',
                    'message': 'PDF generated successfully',
                    'pdf_filename': pdf_filename,
                    'pdf_url': f'/reports/{pdf_filename}'
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'PDF generation failed. Make sure Playwright is installed (pip install playwright && playwright install chromium).'
                }), 500
        except Exception as e:
            import traceback
            traceback.print_exc()  # Print full error to console
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    @app.route('/api/reports/<filename>/email', methods=['POST'])
    def api_email_report(filename):
        """Email a report PDF to specified recipients."""
        try:
            data = request.json or {}
            recipient_emails = data.get('emails', [])
            
            if not recipient_emails:
                return jsonify({'status': 'error', 'message': 'No recipient emails provided'}), 400
            
            # Validate email addresses
            import re
            email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
            invalid_emails = [e for e in recipient_emails if not email_pattern.match(e)]
            if invalid_emails:
                return jsonify({'status': 'error', 'message': f'Invalid email(s): {", ".join(invalid_emails)}'}), 400
            
            reports_dir = PROJECT_ROOT / 'reports'
            source_path = reports_dir / filename
            
            if not source_path.exists():
                return jsonify({'status': 'error', 'message': 'Report not found'}), 404
            
            # Generate PDF if the source is HTML
            if filename.endswith('.html'):
                pdf_name = filename.replace('.html', '.pdf')
                pdf_path = reports_dir / pdf_name
                
                # Generate PDF if it doesn't exist already
                if not pdf_path.exists():
                    report_gen = ReportGenerator(output_dir=str(reports_dir))
                    result_path = report_gen.convert_html_to_pdf(str(source_path))
                    if not result_path:
                        return jsonify({
                            'status': 'error',
                            'message': 'Failed to generate PDF. Make sure xhtml2pdf is installed (pip install xhtml2pdf).'
                        }), 500
                    pdf_path = Path(result_path)
            elif filename.endswith('.pdf'):
                pdf_path = source_path
            else:
                return jsonify({'status': 'error', 'message': 'Unsupported report format'}), 400
            
            # Get website info for the email
            website_name = config.get('website', 'name', default='WordPress Site')
            website_url = config.get_website_url()
            
            # Try to get latest check stats for the email summary
            report_summary = {}
            recent = db.get_recent_checks(1)
            if recent:
                check = recent[0]
                report_summary = {
                    'critical_issues': check.critical_issues or 0,
                    'high_issues': check.high_issues or 0,
                    'medium_issues': check.medium_issues or 0,
                    'low_issues': check.low_issues or 0,
                    'total_issues': (check.critical_issues or 0) + (check.high_issues or 0) + (check.medium_issues or 0) + (check.low_issues or 0),
                    'avg_response_time': 'N/A',
                    'uptime_percentage': round(db.get_uptime_percentage(website_url, days=30), 1),
                    'pages_checked': len(config.get_critical_pages())
                }
            
            # Send email with PDF attachment
            alert_manager = create_alert_manager(config.to_dict())
            result = alert_manager.send_report_email(
                recipient_emails=recipient_emails,
                pdf_path=str(pdf_path),
                report_summary=report_summary,
                website_name=website_name,
                website_url=website_url
            )
            
            if result['status'] == 'success':
                return jsonify(result)
            else:
                return jsonify(result), 500
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    @app.route('/api/email/config', methods=['GET'])
    def api_email_config():
        """Get email configuration status (not credentials)."""
        smtp_username = config.get('alerts', 'email', 'smtp_username', default='') or os.getenv('SMTP_USERNAME', '')
        smtp_password = config.get('alerts', 'email', 'smtp_password', default='') or os.getenv('SMTP_PASSWORD', '')
        recipients = config.get('alerts', 'email', 'recipients', default=[])
        
        return jsonify({
            'configured': bool(smtp_username and smtp_password),
            'smtp_server': config.get('alerts', 'email', 'smtp_server', default='smtp.gmail.com'),
            'from_email': config.get('alerts', 'email', 'from_email', default=''),
            'default_recipients': recipients if isinstance(recipients, list) else []
        })
    
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection."""
        emit('connected', {
            'status': 'ok',
            'is_running': check_state['running']
        })
    
    @socketio.on('start_check')
    def handle_start_check(data):
        """Handle check request via WebSocket."""
        if check_state['running']:
            emit('check_error', {'error': 'A check is already running'})
            return
        
        check_state['running'] = True
        check_state['logs'] = []
        
        def run_check():
            try:
                mode = data.get('mode', 'quick')
                pages = data.get('pages', '')
                limit = data.get('limit', 0)
                use_browser = data.get('use_browser', False)
                headless = data.get('headless', True)
                
                monitor = WordPressMonitor(app.config['MONITOR_CONFIG_PATH'])
                monitor.logger.addHandler(log_handler)
                
                emit('check_progress', {'stage': 'Running', 'message': f'Executing {mode} check...'})
                
                pages_list = [p.strip() for p in pages.split(',')] if pages else None
                
                if mode == 'quick':
                    result = monitor.run_quick_check()
                elif mode == 'fast':
                    result = monitor.run_link_check_only(
                        pages=pages_list,
                        limit=int(limit) if limit else 0,
                        use_browser=use_browser,
                        headless=headless
                    )
                elif mode == 'images':
                    result = monitor.run_image_check_only(
                        pages=pages_list,
                        limit=int(limit) if limit else 0,
                        use_browser=use_browser,
                        headless=headless
                    )
                else:
                    result = monitor.run_all_checks()
                
                monitor.logger.removeHandler(log_handler)
                check_state['running'] = False
                emit('check_complete', result)
                
            except Exception as e:
                check_state['running'] = False
                emit('check_error', {'error': str(e)})
        
        thread = threading.Thread(target=run_check)
        thread.daemon = True
        thread.start()
    
    @socketio.on('get_logs')
    def handle_get_logs():
        """Send current logs to client."""
        emit('logs_update', {'logs': check_state['logs']})
    
    return app, socketio


# Create app and socketio at module level for gunicorn
app, socketio = create_app()


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
