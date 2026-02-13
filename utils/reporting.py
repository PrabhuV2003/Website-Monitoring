"""
Report Generator - Creates HTML/PDF reports for monitoring results.
"""
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from jinja2 import Environment, FileSystemLoader, BaseLoader
from .logger import get_logger

try:
    from xhtml2pdf import pisa
    XHTML2PDF_AVAILABLE = True
except ImportError:
    XHTML2PDF_AVAILABLE = False

class ReportGenerator:
    """Generates monitoring reports in various formats."""
    
    def __init__(self, output_dir: str = "reports", template_dir: str = "templates"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.template_dir = Path(template_dir)
        self.logger = get_logger()
        
        if self.template_dir.exists():
            self.env = Environment(loader=FileSystemLoader(str(self.template_dir)))
        else:
            self.env = Environment(loader=BaseLoader())
    
    def generate_report(self, check_id: str, data: Dict[str, Any], 
                        format: str = "html") -> Optional[str]:
        """Generate a monitoring report."""
        try:
            if format == "html":
                return self._generate_html_report(check_id, data)
            elif format == "pdf":
                return self._generate_pdf_report(check_id, data)
            elif format == "json":
                return self._generate_json_report(check_id, data)
            else:
                self.logger.warning(f"Unsupported format: {format}")
                return None
        except Exception as e:
            self.logger.error(f"Report generation failed: {e}")
            return None
    
    def _generate_html_report(self, check_id: str, data: Dict[str, Any]) -> str:
        html = self._get_html_template(data)
        filename = f"report_{check_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = self.output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        self.logger.info(f"Report saved: {filepath}")
        return str(filepath)
    
    def _generate_json_report(self, check_id: str, data: Dict[str, Any]) -> str:
        import json
        filename = f"report_{check_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        return str(filepath)
    
    def _get_html_template(self, data: Dict[str, Any]) -> str:
        stats = data.get('stats', {})
        issues = data.get('issues', [])
        
        # Filter out "OK" messages that aren't real issues
        filtered_issues = []
        for issue in issues:
            message = issue.get('message', '').lower()
            severity = issue.get('severity', 'info')
            status = issue.get('status', '')
            
            # Skip informational "OK" messages (regardless of severity)
            # These are status updates, not actual problems
            if any(skip_phrase in message for skip_phrase in [
                'no videos found',       # "No videos found on..." - not an error
                'elements ok',           # "SEO elements OK"
                'ok on',                 # General "OK on" messages
                'accessible',            # "robots.txt is accessible"
                'sitemap found',         # "Sitemap found at..."
                'canonical tag ok',      # "Canonical tag OK"
                'structured data found', # "Structured data found"
                'no mixed content',      # "No mixed content found"
                'no javascript errors',  # "No JavaScript errors detected"
                'content unchanged',     # "Content unchanged on..."
            ]):
                # Skip this message - it's informational, not a problem
                continue
            
            # Include this issue in the report
            filtered_issues.append(issue)
        
        issues_html = ""
        for issue in filtered_issues:
            severity = issue.get('severity', 'info')
            color = {'critical': '#dc3545', 'high': '#fd7e14', 'medium': '#ffc107', 'low': '#28a745'}.get(severity, '#6c757d')
            details = issue.get('details', {})
            
            # Build details HTML for broken links
            details_html = ""
            if details:
                broken_links = details.get('broken_links', [])
                if broken_links:
                    details_html = '''
                    <div style="margin-top:10px;padding:10px;background:#fff;border:1px solid #ddd;border-radius:4px;">
                        <strong style="color:#333;">🔗 Broken Links Details:</strong>
                        <table style="width:100%;border-collapse:collapse;margin-top:10px;font-size:12px;">
                            <thead>
                                <tr style="background:#f0f0f0;">
                                    <th style="padding:8px;border:1px solid #ddd;text-align:left;">Link URL</th>
                                    <th style="padding:8px;border:1px solid #ddd;text-align:left;">Link Text</th>
                                    <th style="padding:8px;border:1px solid #ddd;text-align:left;">Status</th>
                                    <th style="padding:8px;border:1px solid #ddd;text-align:left;">Error</th>
                                    <th style="padding:8px;border:1px solid #ddd;text-align:left;">Found On</th>
                                </tr>
                            </thead>
                            <tbody>'''
                    for link in broken_links:
                        link_url = link.get('link_url') or link.get('url', 'Unknown')
                        link_text = link.get('link_text') or link.get('text', 'N/A')
                        status = link.get('status_code') or link.get('status', 'Unknown')
                        status_msg = link.get('status_message', '')
                        found_on = link.get('found_on_page') or link.get('source', 'Unknown')
                        
                        display_url = link_url
                        display_text = link_text
                        
                        details_html += f'''
                                <tr>
                                    <td style="padding:8px;border:1px solid #ddd;word-break:break-all;" title="{link_url}">{display_url}</td>
                                    <td style="padding:8px;border:1px solid #ddd;">{display_text}</td>
                                    <td style="padding:8px;border:1px solid #ddd;color:#dc3545;font-weight:bold;">{status}</td>
                                    <td style="padding:8px;border:1px solid #ddd;">{status_msg}</td>
                                    <td style="padding:8px;border:1px solid #ddd;">{found_on}</td>
                                </tr>'''
                    details_html += '''
                            </tbody>
                        </table>
                    </div>'''
                
                # Show slow links if present
                slow_links = details.get('slow_links', [])
                if slow_links:
                    details_html += '''
                    <div style="margin-top:10px;padding:10px;background:#fffbf0;border:1px solid #ffc107;border-radius:4px;">
                        <strong style="color:#856404;">⏱️ Slow Links:</strong>
                        <ul style="margin:10px 0;padding-left:20px;font-size:12px;">'''
                    for link in slow_links[:10]:
                        link_url = link.get('url', 'Unknown')
                        load_time = link.get('response_time_ms', 'N/A')
                        display_url = link_url
                        details_html += f'<li>{display_url} - <strong>{load_time}ms</strong></li>'
                    details_html += '</ul></div>'
                
                # Show broken images if present
                broken_images = details.get('broken_images', [])
                if broken_images:
                    details_html += '''
                    <div style="margin-top:10px;padding:10px;background:#fff0f0;border:1px solid #dc3545;border-radius:4px;">
                        <strong style="color:#dc3545;">🖼️ Broken Images:</strong>
                        <table style="width:100%;border-collapse:collapse;margin-top:10px;font-size:12px;">
                            <thead>
                                <tr style="background:#f0f0f0;">
                                    <th style="padding:8px;border:1px solid #ddd;text-align:left;">Image URL</th>
                                    <th style="padding:8px;border:1px solid #ddd;text-align:left;">Alt Text</th>
                                    <th style="padding:8px;border:1px solid #ddd;text-align:left;">Status</th>
                                    <th style="padding:8px;border:1px solid #ddd;text-align:left;">Error</th>
                                    <th style="padding:8px;border:1px solid #ddd;text-align:left;">Found On</th>
                                </tr>
                            </thead>
                            <tbody>'''
                    for img in broken_images[:20]:
                        img_url = img.get('image_url', 'Unknown')
                        alt_text = img.get('alt_text', 'N/A')
                        status = img.get('status_code', 'Unknown')
                        status_msg = img.get('status_message', '')
                        found_on = img.get('found_on_page', 'Unknown')
                        
                        display_url = img_url
                        display_alt = alt_text
                        
                        details_html += f'''
                                <tr>
                                    <td style="padding:8px;border:1px solid #ddd;word-break:break-all;" title="{img_url}">{display_url}</td>
                                    <td style="padding:8px;border:1px solid #ddd;">{display_alt}</td>
                                    <td style="padding:8px;border:1px solid #ddd;color:#dc3545;font-weight:bold;">{status}</td>
                                    <td style="padding:8px;border:1px solid #ddd;">{status_msg}</td>
                                    <td style="padding:8px;border:1px solid #ddd;">{found_on}</td>
                                </tr>'''
                    details_html += '''
                            </tbody>
                        </table>
                    </div>'''
                
                # Show slow images if present
                slow_images = details.get('slow_images', [])
                if slow_images:
                    details_html += '''
                    <div style="margin-top:10px;padding:10px;background:#fffbf0;border:1px solid #ffc107;border-radius:4px;">
                        <strong style="color:#856404;">⏱️ Slow Images (>3s):</strong>
                        <ul style="margin:10px 0;padding-left:20px;font-size:12px;">'''
                    for img in slow_images[:10]:
                        img_url = img.get('image_url', 'Unknown')
                        load_time = img.get('load_time_ms', 'N/A')
                        display_url = img_url
                        details_html += f'<li>{display_url} - <strong>{load_time}ms</strong></li>'
                    details_html += '</ul></div>'
                
                # Show missing alt images if present
                missing_alt_images = details.get('missing_alt_images', [])
                if missing_alt_images:
                    details_html += '''
                    <div style="margin-top:10px;padding:10px;background:#e7f3ff;border:1px solid #0d6efd;border-radius:4px;">
                        <strong style="color:#0d6efd;">🏷️ Images Missing Alt Text (SEO/Accessibility):</strong>
                        <ul style="margin:10px 0;padding-left:20px;font-size:12px;">'''
                    for img in missing_alt_images[:10]:
                        img_url = img.get('image_url', 'Unknown')
                        display_url = img_url
                        details_html += f'<li style="word-break:break-all;">{display_url}</li>'
                    if len(missing_alt_images) > 10:
                        details_html += f'<li><em>...and {len(missing_alt_images) - 10} more</em></li>'
                    details_html += '</ul></div>'
                
                # Show all checked links for verification
                all_checked_links = details.get('all_checked_links', [])
                if all_checked_links:
                    details_html += f'''
                    <details style="margin-top:10px;">
                        <summary style="cursor:pointer;padding:10px;background:#f0f8ff;border:1px solid #4a90d9;border-radius:4px;color:#0d6efd;font-weight:bold;">
                            📋 All Checked Links ({len(all_checked_links)} links) - Click to expand
                        </summary>
                        <div style="padding:10px;background:#fafafa;border:1px solid #ddd;border-top:none;border-radius:0 0 4px 4px;max-height:400px;overflow-y:auto;">
                            <table style="width:100%;border-collapse:collapse;font-size:11px;">
                                <thead>
                                    <tr style="background:#e8e8e8;position:sticky;top:0;">
                                        <th style="padding:6px;border:1px solid #ccc;text-align:left;width:5%;">#</th>
                                        <th style="padding:6px;border:1px solid #ccc;text-align:left;width:50%;">Link URL</th>
                                        <th style="padding:6px;border:1px solid #ccc;text-align:left;width:25%;">Link Text</th>
                                        <th style="padding:6px;border:1px solid #ccc;text-align:left;width:10%;">Status</th>
                                        <th style="padding:6px;border:1px solid #ccc;text-align:left;width:10%;">Time</th>
                                    </tr>
                                </thead>
                                <tbody>'''
                    for idx, link in enumerate(all_checked_links, 1):
                        link_url = link.get('url') or link.get('link_url', 'Unknown')
                        link_text = link.get('text') or link.get('link_text', 'N/A')
                        status = link.get('status_code', 'OK')
                        resp_time = link.get('response_time_ms', '-')
                        
                        # Color code based on status
                        if isinstance(status, int) and status < 400:
                            status_color = '#28a745'
                            status_display = f'✅ {status}'
                        else:
                            status_color = '#dc3545'
                            status_display = f'❌ {status}'
                        
                        display_url = link_url
                        display_text = link_text
                        
                        details_html += f'''
                                    <tr>
                                        <td style="padding:4px 6px;border:1px solid #ddd;">{idx}</td>
                                        <td style="padding:4px 6px;border:1px solid #ddd;word-break:break-all;" title="{link_url}">{display_url}</td>
                                        <td style="padding:4px 6px;border:1px solid #ddd;">{display_text}</td>
                                        <td style="padding:4px 6px;border:1px solid #ddd;color:{status_color};font-weight:bold;">{status_display}</td>
                                        <td style="padding:4px 6px;border:1px solid #ddd;">{resp_time}ms</td>
                                    </tr>'''
                    details_html += '''
                                </tbody>
                            </table>
                        </div>
                    </details>'''
            
            issues_html += f'''
            <div style="border-left:4px solid {color};padding:10px;margin:10px 0;background:#f8f9fa;border-radius:0 4px 4px 0;">
                <strong style="color:{color}">[{severity.upper()}]</strong> {issue.get('message', '')}
                <div style="font-size:12px;color:#666;margin-top:5px;">
                    {issue.get('monitor', '')} | {issue.get('url', '')}
                </div>
                {details_html}
            </div>'''
        
        return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>WordPress Monitor Report</title>
<style>
body{{font-family:Arial,sans-serif;margin:0;padding:20px;background:#f5f5f5}}
.container{{max-width:900px;margin:auto;background:white;padding:20px;border-radius:8px;box-shadow:0 2px 4px rgba(0,0,0,0.1)}}
.header{{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;padding:30px;border-radius:8px;margin-bottom:20px}}
.stats{{display:grid;grid-template-columns:repeat(4,1fr);gap:15px;margin:20px 0}}
.stat{{background:#f8f9fa;padding:20px;border-radius:8px;text-align:center}}
.stat-value{{font-size:24px;font-weight:bold;color:#333}}
.stat-label{{font-size:12px;color:#666;margin-top:5px}}
.critical{{color:#dc3545}}.high{{color:#fd7e14}}.medium{{color:#ffc107}}.low{{color:#28a745}}
</style></head><body>
<div class="container">
<div class="header">
<h1>WordPress Monitor Report</h1>
<p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
<p>Website: {stats.get('website_url', 'N/A')}</p>
</div>
<div class="stats">
<div class="stat"><div class="stat-value critical">{stats.get('critical_issues', 0)}</div><div class="stat-label">Critical</div></div>
<div class="stat"><div class="stat-value high">{stats.get('high_issues', 0)}</div><div class="stat-label">High</div></div>
<div class="stat"><div class="stat-value medium">{stats.get('medium_issues', 0)}</div><div class="stat-label">Medium</div></div>
<div class="stat"><div class="stat-value low">{stats.get('low_issues', 0)}</div><div class="stat-label">Low</div></div>
</div>
<h2>Issues Found</h2>
{issues_html if issues_html else '<p style="color:#28a745">No issues found!</p>'}
<h2>Performance Summary</h2>
<table style="width:100%;border-collapse:collapse">
<tr><td style="padding:10px;border:1px solid #ddd">Response Time</td><td style="padding:10px;border:1px solid #ddd">{stats.get('avg_response_time', 'N/A')} ms</td></tr>
<tr><td style="padding:10px;border:1px solid #ddd">Uptime</td><td style="padding:10px;border:1px solid #ddd">{stats.get('uptime_percentage', 'N/A')}%</td></tr>
<tr><td style="padding:10px;border:1px solid #ddd">Pages Checked</td><td style="padding:10px;border:1px solid #ddd">{stats.get('pages_checked', 0)}</td></tr>
<tr><td style="padding:10px;border:1px solid #ddd">Links Checked</td><td style="padding:10px;border:1px solid #ddd">{stats.get('links_checked', 0)}</td></tr>
</table>
</div></body></html>'''
    
    def _generate_pdf_report(self, check_id: str, data: Dict[str, Any]) -> Optional[str]:
        """Generate a PDF report by converting the HTML report using Playwright.
        This preserves all styling, gradients, and modern CSS."""
        try:
            # First generate the HTML report
            html_path = self._generate_html_report(check_id, data)
            if not html_path:
                return None
            
            # Convert HTML to PDF
            pdf_path = self.convert_html_to_pdf(html_path)
            return pdf_path
        except Exception as e:
            self.logger.error(f"PDF generation failed: {e}")
            return None
    
    def convert_html_to_pdf(self, html_filepath: str) -> Optional[str]:
        """Convert an existing HTML report file to PDF using Playwright.
        This preserves all CSS styling including gradients, flexbox, animations, etc."""
        try:
            from playwright.sync_api import sync_playwright
            
            html_path = Path(html_filepath)
            if not html_path.exists():
                self.logger.error(f"HTML file not found: {html_filepath}")
                return None
            
            pdf_filename = html_path.stem + '.pdf'
            pdf_filepath = html_path.parent / pdf_filename
            
            self.logger.info(f"Starting PDF generation for: {html_path}")
            
            # Fix HOME environment variable for Playwright on Windows
            # Playwright requires HOME to be set to find browser installations
            import os
            if 'HOME' not in os.environ and 'USERPROFILE' in os.environ:
                os.environ['HOME'] = os.environ['USERPROFILE']
                self.logger.info(f"Set HOME environment variable to: {os.environ['HOME']}")
            
            # Use Playwright to render HTML and save as PDF
            with sync_playwright() as p:
                self.logger.info("Launching Chromium browser...")
                browser = p.chromium.launch()
                page = browser.new_page()
                
                # Load the HTML file
                file_url = f'file:///{html_path.absolute().as_posix()}'
                self.logger.info(f"Loading HTML file: {file_url}")
                page.goto(file_url)
                
                # Wait for page to fully load
                self.logger.info("Waiting for page to load...")
                page.wait_for_load_state('networkidle')
                
                # Generate PDF with proper settings
                self.logger.info(f"Generating PDF: {pdf_filepath}")
                page.pdf(
                    path=str(pdf_filepath),
                    format='A4',
                    print_background=True,  # This preserves gradients and background colors!
                    margin={
                        'top': '15mm',
                        'right': '15mm',
                        'bottom': '15mm',
                        'left': '15mm'
                    }
                )
                
                browser.close()
                self.logger.info("Browser closed")
            
            self.logger.info(f"PDF generated from HTML: {pdf_filepath}")
            return str(pdf_filepath)
            
        except ImportError as ie:
            import traceback
            self.logger.error(f"Playwright import failed: {ie}")
            traceback.print_exc()
            return None
        except Exception as e:
            import traceback
            self.logger.error(f"HTML to PDF conversion failed: {e}")
            traceback.print_exc()
            return None
    
    def cleanup_old_reports(self, keep_days: int = 30):
        """Remove reports older than specified days."""
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=keep_days)
        for file in self.output_dir.glob("report_*"):
            if file.stat().st_mtime < cutoff.timestamp():
                file.unlink()
                self.logger.info(f"Deleted old report: {file}")
