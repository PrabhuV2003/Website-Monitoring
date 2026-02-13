"""
Alert Manager - Handles sending alerts via email, Slack, Discord.
"""
import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import requests
from .logger import get_logger

class AlertManager:
    """Manages alert notifications across multiple channels."""
    
    SEVERITY_COLORS = {
        'critical': '#FF0000', 'high': '#FF6B00',
        'medium': '#FFD700', 'low': '#00FF00', 'info': '#0099FF'
    }
    SEVERITY_EMOJI = {
        'critical': '🚨', 'high': '⚠️', 'medium': '⚡', 'low': 'ℹ️', 'info': '📝'
    }
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_logger()
        self.email_config = config.get('email', {})
        self.slack_config = config.get('slack', {})
        self.discord_config = config.get('discord', {})
    
    def send_alert(self, title: str, message: str, severity: str = 'info',
                   details: Optional[Dict] = None, attachments: Optional[List[str]] = None,
                   check_id: Optional[str] = None):
        """Send an alert through all enabled channels."""
        self.logger.info(f"Sending {severity} alert: {title}")
        if self.email_config.get('enabled'):
            self._send_email_alert(title, message, severity, details)
        if self.slack_config.get('enabled'):
            self._send_slack_alert(title, message, severity, details)
        if self.discord_config.get('enabled'):
            self._send_discord_alert(title, message, severity, details)
    
    def _send_email_alert(self, title: str, message: str, severity: str, details: Optional[Dict] = None):
        try:
            smtp_server = self.email_config.get('smtp_server', 'smtp.gmail.com')
            smtp_port = self.email_config.get('smtp_port', 587)
            smtp_username = self.email_config.get('smtp_username') or os.getenv('SMTP_USERNAME')
            smtp_password = self.email_config.get('smtp_password') or os.getenv('SMTP_PASSWORD')
            from_email = self.email_config.get('from_email', smtp_username)
            recipients = self.email_config.get('recipients', [])
            if not smtp_username or not smtp_password or not recipients:
                return
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"[{severity.upper()}] {title}"
            msg['From'] = from_email
            msg['To'] = ', '.join(recipients)
            
            color = self.SEVERITY_COLORS.get(severity, '#333')
            html = f'<div style="font-family:Arial;max-width:600px;margin:auto;"><div style="background:{color};color:white;padding:20px;"><h2>{title}</h2></div><div style="padding:20px;background:#f9f9f9;"><p>{message}</p></div></div>'
            msg.attach(MIMEText(html, 'html'))
            
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
            self.logger.info(f"Email sent to {recipients}")
        except Exception as e:
            self.logger.error(f"Email failed: {e}")
    
    def send_report_email(self, recipient_emails: List[str], pdf_path: str, 
                          report_summary: Optional[Dict] = None,
                          website_name: str = "WordPress Site",
                          website_url: str = "") -> Dict[str, Any]:
        """Send PDF report as email attachment to client.
        
        Args:
            recipient_emails: List of client email addresses
            pdf_path: Path to the PDF report file
            report_summary: Optional dict with stats (critical_issues, high_issues, etc.)
            website_name: Name of the website
            website_url: URL of the website
            
        Returns:
            Dict with status and message
        """
        try:
            smtp_server = self.email_config.get('smtp_server', 'smtp.gmail.com')
            smtp_port = self.email_config.get('smtp_port', 587)
            smtp_username = self.email_config.get('smtp_username') or os.getenv('SMTP_USERNAME')
            smtp_password = self.email_config.get('smtp_password') or os.getenv('SMTP_PASSWORD')
            from_email = self.email_config.get('from_email', smtp_username)
            
            if not smtp_username or not smtp_password:
                return {'status': 'error', 'message': 'SMTP credentials not configured. Set SMTP_USERNAME and SMTP_PASSWORD environment variables.'}
            
            if not recipient_emails:
                return {'status': 'error', 'message': 'No recipient email addresses provided.'}
            
            pdf_file = Path(pdf_path)
            if not pdf_file.exists():
                return {'status': 'error', 'message': f'PDF file not found: {pdf_path}'}
            
            # Build the email
            msg = MIMEMultipart('mixed')
            msg['Subject'] = f"🌐 Website Health Report — {website_name} ({datetime.now().strftime('%Y-%m-%d')})"
            msg['From'] = from_email
            msg['To'] = ', '.join(recipient_emails)
            
            # Build summary stats for the email body
            stats = report_summary or {}
            critical = stats.get('critical_issues', 0)
            high = stats.get('high_issues', 0)
            medium = stats.get('medium_issues', 0)
            low = stats.get('low_issues', 0)
            total_issues = stats.get('total_issues', critical + high + medium + low)
            
            # Health score
            if total_issues == 0:
                health_score = 100
                health_color = '#28a745'
                health_label = 'Excellent'
                health_emoji = '🟢'
            elif critical > 0:
                health_score = max(0, 100 - (critical * 25) - (high * 10))
                health_color = '#dc3545'
                health_label = 'Critical'
                health_emoji = '🔴'
            elif high > 0:
                health_score = max(20, 100 - (high * 15) - (medium * 5))
                health_color = '#fd7e14'
                health_label = 'Needs Attention'
                health_emoji = '🟠'
            else:
                health_score = max(60, 100 - (medium * 5) - (low * 2))
                health_color = '#ffc107' if health_score < 80 else '#28a745'
                health_label = 'Good' if health_score >= 80 else 'Fair'
                health_emoji = '🟡' if health_score < 80 else '🟢'
            
            html_body = f'''
            <div style="font-family: Arial, Helvetica, sans-serif; max-width: 600px; margin: auto; background: #f5f5f5; padding: 0;">
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 8px 8px 0 0;">
                    <h1 style="margin: 0 0 8px 0; font-size: 22px; background: #0000">🌐 Website Health Report</h1>
                    <p style="margin: 4px 0; font-size: 14px; opacity: 0.9;"><strong>{website_name}</strong></p>
                    <p style="margin: 4px 0; font-size: 12px; opacity: 0.8;">{website_url}</p>
                    <p style="margin: 4px 0; font-size: 12px; opacity: 0.8;">Report Date: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                </div>
                
                <!-- Health Score -->
                <div style="background: white; padding: 25px; text-align: center; border-bottom: 1px solid #eee;">
                    <div style="font-size: 14px; color: #666; margin-bottom: 8px;">Overall Health Score</div>
                    <div style="font-size: 48px; font-weight: bold; color: {health_color};">{health_emoji} {health_score}/100</div>
                    <div style="font-size: 16px; color: {health_color}; font-weight: 600; margin-top: 5px;">{health_label}</div>
                </div>
                
                <!-- Issue Summary -->
                <div style="background: white; padding: 20px; border-bottom: 1px solid #eee;">
                    <h2 style="font-size: 16px; color: #333; margin: 0 0 15px 0;">📊 Issue Summary</h2>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 10px; text-align: center; background: #fff5f5; border-radius: 6px;">
                                <div style="font-size: 24px; font-weight: bold; color: #dc3545;">{critical}</div>
                                <div style="font-size: 11px; color: #666; text-transform: uppercase;">Critical</div>
                            </td>
                            <td style="width: 8px;"></td>
                            <td style="padding: 10px; text-align: center; background: #fff8f0; border-radius: 6px;">
                                <div style="font-size: 24px; font-weight: bold; color: #fd7e14;">{high}</div>
                                <div style="font-size: 11px; color: #666; text-transform: uppercase;">High</div>
                            </td>
                            <td style="width: 8px;"></td>
                            <td style="padding: 10px; text-align: center; background: #fffbf0; border-radius: 6px;">
                                <div style="font-size: 24px; font-weight: bold; color: #ffc107;">{medium}</div>
                                <div style="font-size: 11px; color: #666; text-transform: uppercase;">Medium</div>
                            </td>
                            <td style="width: 8px;"></td>
                            <td style="padding: 10px; text-align: center; background: #f0fff4; border-radius: 6px;">
                                <div style="font-size: 24px; font-weight: bold; color: #28a745;">{low}</div>
                                <div style="font-size: 11px; color: #666; text-transform: uppercase;">Low</div>
                            </td>
                        </tr>
                    </table>
                </div>
                
                <!-- Performance -->
                <div style="background: white; padding: 20px; border-bottom: 1px solid #eee;">
                    <h2 style="font-size: 16px; color: #333; margin: 0 0 12px 0;">⚡ Performance</h2>
                    <table style="width: 100%; font-size: 13px;">
                        <tr><td style="padding: 6px 0; color: #666;">Response Time</td><td style="padding: 6px 0; font-weight: 600; text-align: right;">{stats.get('avg_response_time', 'N/A')} ms</td></tr>
                        <tr><td style="padding: 6px 0; color: #666;">Uptime</td><td style="padding: 6px 0; font-weight: 600; text-align: right;">{stats.get('uptime_percentage', 'N/A')}%</td></tr>
                        <tr><td style="padding: 6px 0; color: #666;">Pages Checked</td><td style="padding: 6px 0; font-weight: 600; text-align: right;">{stats.get('pages_checked', 0)}</td></tr>
                    </table>
                </div>
                
                <!-- CTA -->
                <div style="background: white; padding: 25px; text-align: center; border-bottom: 1px solid #eee;">
                    <p style="color: #666; font-size: 13px; margin: 0 0 10px 0;">📎 The full detailed report is attached as a PDF.</p>
                    <p style="color: #999; font-size: 11px; margin: 0;">Please review the attached PDF for the complete breakdown of all issues found.</p>
                </div>
                
                <!-- Footer -->
                <div style="padding: 20px; text-align: center; border-radius: 0 0 8px 8px;">
                    <p style="color: #999; font-size: 11px; margin: 0;">Generated by <strong>WordPress Monitor</strong> by Nevas Technologies</p>
                    <p style="color: #bbb; font-size: 10px; margin: 5px 0 0 0;">This is an automated report. Please do not reply to this email.</p>
                </div>
            </div>
            '''
            
            # Create HTML part and attach to a related alternative
            html_part = MIMEMultipart('alternative')
            text_part = MIMEText(
                f"Website Health Report for {website_name}\n"
                f"Health Score: {health_score}/100 ({health_label})\n"
                f"Issues: {critical} Critical, {high} High, {medium} Medium, {low} Low\n\n"
                f"The full report is attached as a PDF.\n",
                'plain'
            )
            html_part.attach(text_part)
            html_part.attach(MIMEText(html_body, 'html'))
            msg.attach(html_part)
            
            # Attach PDF file
            with open(pdf_file, 'rb') as f:
                pdf_attachment = MIMEBase('application', 'pdf')
                pdf_attachment.set_payload(f.read())
                encoders.encode_base64(pdf_attachment)
                pdf_attachment.add_header(
                    'Content-Disposition', 
                    'attachment', 
                    filename=pdf_file.name
                )
                msg.attach(pdf_attachment)
            
            # Send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
            
            self.logger.info(f"Report email sent to {recipient_emails}")
            return {
                'status': 'success', 
                'message': f'Report emailed successfully to {", ".join(recipient_emails)}',
                'recipients': recipient_emails
            }
            
        except smtplib.SMTPAuthenticationError:
            self.logger.error("SMTP authentication failed")
            return {'status': 'error', 'message': 'SMTP authentication failed. Check your username and password (use App Password for Gmail).'}
        except smtplib.SMTPException as e:
            self.logger.error(f"SMTP error: {e}")
            return {'status': 'error', 'message': f'SMTP error: {str(e)}'}
        except Exception as e:
            self.logger.error(f"Report email failed: {e}")
            return {'status': 'error', 'message': f'Failed to send email: {str(e)}'}
    
    def _send_slack_alert(self, title: str, message: str, severity: str, details: Optional[Dict] = None):
        try:
            webhook_url = self.slack_config.get('webhook_url') or os.getenv('SLACK_WEBHOOK_URL')
            if not webhook_url:
                return
            payload = {
                'attachments': [{
                    'color': self.SEVERITY_COLORS.get(severity, '#333'),
                    'title': f"{self.SEVERITY_EMOJI.get(severity, '')} {title}",
                    'text': message,
                    'footer': 'WordPress Monitor'
                }]
            }
            requests.post(webhook_url, json=payload, timeout=10)
            self.logger.info("Slack alert sent")
        except Exception as e:
            self.logger.error(f"Slack failed: {e}")
    
    def _send_discord_alert(self, title: str, message: str, severity: str, details: Optional[Dict] = None):
        try:
            webhook_url = self.discord_config.get('webhook_url') or os.getenv('DISCORD_WEBHOOK_URL')
            if not webhook_url:
                return
            color = int(self.SEVERITY_COLORS.get(severity, '#333').replace('#', ''), 16)
            payload = {
                'embeds': [{
                    'title': f"{self.SEVERITY_EMOJI.get(severity, '')} {title}",
                    'description': message,
                    'color': color,
                    'footer': {'text': 'WordPress Monitor'}
                }]
            }
            requests.post(webhook_url, json=payload, timeout=10)
            self.logger.info("Discord alert sent")
        except Exception as e:
            self.logger.error(f"Discord failed: {e}")
    
    def send_downtime_alert(self, url: str, error: str, retry_count: int = 0):
        self.send_alert("WEBSITE DOWN", f"{url} is not responding: {error}", 'critical',
                       {'URL': url, 'Error': error, 'Retries': retry_count})
    
    def send_recovery_alert(self, url: str, downtime_duration: float):
        self.send_alert("WEBSITE RECOVERED", f"{url} is back online", 'info',
                       {'URL': url, 'Downtime': f"{downtime_duration:.1f} min"})
    
    def send_ssl_expiry_alert(self, domain: str, days: int):
        severity = 'critical' if days <= 7 else 'high' if days <= 30 else 'medium'
        self.send_alert("SSL Expiring", f"SSL for {domain} expires in {days} days", severity)

def create_alert_manager(config: Dict[str, Any]) -> AlertManager:
    return AlertManager(config.get('alerts', {}))
