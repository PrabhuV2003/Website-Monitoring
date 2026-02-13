"""
WordPress Monitor CLI - Rich command-line interface.
"""
import os
import sys
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    os.environ['PYTHONIOENCODING'] = 'utf-8'

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
from rich import print as rprint

from main import WordPressMonitor
from utils.config_loader import ConfigLoader

console = Console()


@click.group()
@click.version_option(version='1.0.0', prog_name='WordPress Monitor')
def cli():
    """WordPress Monitor - Automated website monitoring tool."""
    pass


@cli.command()
@click.option('--config', '-c', default='config/config.yaml', help='Configuration file path')
@click.option('--url', '-u', help='Website URL to monitor')
@click.option('--quick', '-q', is_flag=True, help='Quick uptime check only')
@click.option('--fast', '-f', is_flag=True, help='Fast mode: only check anchor links (skip other monitors)')
@click.option('--images', '-i', is_flag=True, help='Image mode: only check images (broken, slow, missing alt)')
@click.option('--videos', '-v', is_flag=True, help='Video mode: check embedded videos (YouTube, Vimeo, etc.)')
@click.option('--pages', '-p', help='Comma-separated list of pages to check (e.g., /,/about/,/contact/)')
@click.option('--limit', '-l', type=int, default=0, help='Limit number of items to check per page (0=unlimited)')
@click.option('--browser', '-b', is_flag=True, help='Use browser instead of HTTP requests (slower but more accurate)')
@click.option('--headless/--visible', default=True, help='Run browser in headless mode (invisible) or visible mode')
@click.option('--no-report', is_flag=True, help='Skip report generation')
@click.option('--no-alerts', is_flag=True, help='Disable alerts')
@click.option('--ignore-header', is_flag=True, help='Ignore links/images in header and navigation')
@click.option('--ignore-footer', is_flag=True, help='Ignore links/images in footer')
@click.option('--main-content-only', is_flag=True, help='Only check main content area (most restrictive)')
def check(config, url, quick, fast, images, videos, pages, limit, browser, headless, no_report, no_alerts,
          ignore_header, ignore_footer, main_content_only):
    """Run monitoring checks on the website.
    
    Modes:
      --quick    : Quick uptime check only
      --fast     : Check anchor links only
      --images   : Check images only
      --videos   : Check embedded videos only (YouTube, Vimeo, HTML5)
      (no mode)  : Full comprehensive check
    
    Browser options:
      --browser  : Use Selenium browser instead of HTTP requests
      --visible  : Show browser window (use with --browser)
    
    Content filtering:
      --ignore-header      : Skip header/navigation elements
      --ignore-footer      : Skip footer elements
      --main-content-only  : Only check <main>, <article>, or .content
    """
    if url:
        os.environ['WP_MONITOR_URL'] = url
    
    console.print(Panel.fit(
        "[bold blue]WordPress Monitor[/bold blue]\n"
        "Automated Website Monitoring Tool",
        border_style="blue"
    ))
    
    try:
        monitor = WordPressMonitor(config)
        
        # Show browser mode info
        if browser:
            mode_text = "visible browser" if not headless else "headless browser"
            console.print(f"[dim]Mode: {mode_text}[/dim]")
        else:
            console.print(f"[dim]Mode: HTTP requests (fast)[/dim]")
        
        if quick:
            console.print("\n[yellow]Running quick uptime check...[/yellow]\n")
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Checking website...", total=None)
                result = monitor.run_quick_check()
                progress.update(task, completed=True)
        elif fast:
            # Fast mode: only check links
            console.print(f"\n[cyan]Running FAST mode (links only)...[/cyan]")
            console.print(f"[dim]Target: {monitor.base_url}[/dim]")
            if pages:
                console.print(f"[dim]Pages: {pages}[/dim]")
            if limit:
                console.print(f"[dim]Link limit per page: {limit}[/dim]")
            if ignore_header or ignore_footer or main_content_only:
                scope_text = "main content only" if main_content_only else ", ".join(filter(None, [
                    "no header" if ignore_header else None,
                    "no footer" if ignore_footer else None
                ]))
                console.print(f"[dim]Scope: {scope_text}[/dim]")
            console.print()
            
            result = monitor.run_link_check_only(
                pages=pages.split(',') if pages else None,
                limit=limit,
                generate_report=not no_report,
                use_browser=browser,
                headless=headless,
                ignore_header=ignore_header,
                ignore_footer=ignore_footer,
                main_content_only=main_content_only
            )
        elif images:
            # Image mode: only check images
            console.print(f"\n[magenta]Running IMAGE mode (images only)...[/magenta]")
            console.print(f"[dim]Target: {monitor.base_url}[/dim]")
            if pages:
                console.print(f"[dim]Pages: {pages}[/dim]")
            if limit:
                console.print(f"[dim]Image limit per page: {limit}[/dim]")
            console.print(f"[dim]Checking: broken images, slow loading, missing alt text[/dim]")
            if ignore_header or ignore_footer or main_content_only:
                scope_text = "main content only" if main_content_only else ", ".join(filter(None, [
                    "no header" if ignore_header else None,
                    "no footer" if ignore_footer else None
                ]))
                console.print(f"[dim]Scope: {scope_text}[/dim]")
            console.print()
            
            result = monitor.run_image_check_only(
                pages=pages.split(',') if pages else None,
                limit=limit,
                generate_report=not no_report,
                use_browser=browser,
                headless=headless,
                ignore_header=ignore_header,
                ignore_footer=ignore_footer,
                main_content_only=main_content_only
            )
        elif videos:
            # Video mode: only check videos
            console.print(f"\n[red]Running VIDEO mode (videos only)...[/red]")
            console.print(f"[dim]Target: {monitor.base_url}[/dim]")
            if pages:
                console.print(f"[dim]Pages: {pages}[/dim]")
            console.print(f"[dim]Checking: YouTube, Vimeo, HTML5 videos[/dim]")
            console.print()
            
            result = monitor.run_video_check_only(
                pages=pages.split(',') if pages else None,
                generate_report=not no_report,
                use_browser=browser,
                headless=headless
            )
        else:
            console.print(f"\n[yellow]Starting full monitoring check...[/yellow]")
            console.print(f"[dim]Target: {monitor.base_url}[/dim]")
            if pages:
                console.print(f"[dim]Pages: {pages}[/dim]")
            if ignore_header or ignore_footer or main_content_only:
                scope_text = "main content only" if main_content_only else ", ".join(filter(None, [
                    "no header" if ignore_header else None,
                    "no footer" if ignore_footer else None
                ]))
                console.print(f"[dim]Scope: {scope_text}[/dim]")
            console.print()
            
            result = monitor.run_all_checks(
                generate_report=not no_report,
                pages=pages.split(',') if pages else None,
                use_browser=browser,
                headless=headless,
                ignore_header=ignore_header,
                ignore_footer=ignore_footer,
                main_content_only=main_content_only
            )
        
        # Display results
        _display_results(result)
        
        if result.get('critical_issues', 0) > 0:
            sys.exit(1)
            
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.option('--config', '-c', default='config/config.yaml', help='Configuration file path')
def status(config):
    """Show current monitoring status and recent checks."""
    try:
        from utils.database import get_database
        
        config_loader = ConfigLoader(config)
        db = get_database(config_loader.to_dict())
        
        recent_checks = db.get_recent_checks(5)
        
        console.print(Panel.fit(
            "[bold]Recent Monitoring Checks[/bold]",
            border_style="blue"
        ))
        
        if not recent_checks:
            console.print("[dim]No checks recorded yet.[/dim]")
            return
        
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Check ID", style="dim")
        table.add_column("Time")
        table.add_column("Status")
        table.add_column("Critical", justify="center")
        table.add_column("High", justify="center")
        table.add_column("Medium", justify="center")
        table.add_column("Low", justify="center")
        
        for check in recent_checks:
            status_color = "green" if check.critical_issues == 0 else "red"
            table.add_row(
                check.check_id[:20],
                check.start_time.strftime('%Y-%m-%d %H:%M') if check.start_time else '-',
                f"[{status_color}]{check.status}[/{status_color}]",
                f"[red]{check.critical_issues}[/red]" if check.critical_issues else "0",
                f"[orange1]{check.high_issues}[/orange1]" if check.high_issues else "0",
                f"[yellow]{check.medium_issues}[/yellow]" if check.medium_issues else "0",
                str(check.low_issues or 0)
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")


@cli.command()
@click.option('--config', '-c', default='config/config.yaml', help='Configuration file path')
def links(config):
    """Show broken links from recent checks."""
    try:
        from utils.database import get_database
        
        config_loader = ConfigLoader(config)
        db = get_database(config_loader.to_dict())
        
        broken_links = db.get_broken_links(20)
        
        console.print(Panel.fit(
            "[bold]Broken Links[/bold]",
            border_style="red"
        ))
        
        if not broken_links:
            console.print("[green]No broken links found![/green]")
            return
        
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Source", style="dim", max_width=40)
        table.add_column("Target", max_width=50)
        table.add_column("Status", justify="center")
        table.add_column("Times", justify="center")
        
        for link in broken_links:
            table.add_row(
                link.source_url[-40:] if link.source_url else '-',
                link.target_url[-50:] if link.target_url else '-',
                f"[red]{link.status_code or link.error_type}[/red]",
                str(link.times_detected)
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")


@cli.command()
@click.option('--host', '-h', default='0.0.0.0', help='Dashboard host')
@click.option('--port', '-p', default=5000, type=int, help='Dashboard port')
@click.option('--config', '-c', default='config/config.yaml', help='Configuration file path')
def dashboard(host, port, config):
    """Start the web dashboard."""
    console.print(Panel.fit(
        f"[bold blue]Starting Dashboard[/bold blue]\n"
        f"http://{host}:{port}",
        border_style="blue"
    ))
    
    try:
        from dashboard.app import create_app
        app = create_app(config)
        app.run(host=host, port=port, debug=False)
    except ImportError:
        console.print("[yellow]Dashboard dependencies not installed.[/yellow]")
        console.print("Run: pip install flask flask-socketio")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")


@cli.command()
@click.option('--config', '-c', default='config/config.yaml', help='Configuration file path')
def schedule(config):
    """Run the scheduler for automated checks."""
    console.print(Panel.fit(
        "[bold blue]WordPress Monitor Scheduler[/bold blue]\n"
        "Running automated checks...",
        border_style="blue"
    ))
    
    try:
        from scheduler import run_scheduler
        run_scheduler(config)
    except ImportError:
        console.print("[yellow]Scheduler not available. Using basic scheduling.[/yellow]")
        _basic_scheduler(config)
    except KeyboardInterrupt:
        console.print("\n[yellow]Scheduler stopped.[/yellow]")


def _basic_scheduler(config):
    """Basic scheduler using time.sleep."""
    import time
    from datetime import datetime
    
    monitor = WordPressMonitor(config)
    
    console.print("[dim]Press Ctrl+C to stop[/dim]\n")
    
    while True:
        now = datetime.now()
        console.print(f"[dim][{now.strftime('%Y-%m-%d %H:%M:%S')}] Running check...[/dim]")
        
        try:
            result = monitor.run_all_checks()
            _display_results(result, compact=True)
        except Exception as e:
            console.print(f"[red]Check failed: {e}[/red]")
        
        # Wait for next check (default: 1 hour)
        console.print("[dim]Next check in 1 hour...[/dim]\n")
        time.sleep(3600)


def _display_results(result, compact=False):
    """Display check results in a formatted table."""
    if 'error' in result:
        console.print(f"[bold red]Error:[/bold red] {result['error']}")
        return
    
    # Summary panel
    total = result.get('total_issues', 0)
    critical = result.get('critical_issues', 0)
    high = result.get('high_issues', 0)
    medium = result.get('medium_issues', 0)
    low = result.get('low_issues', 0)
    
    if critical > 0:
        status_color = "red"
        status_text = "CRITICAL ISSUES"
    elif high > 0:
        status_color = "orange1"
        status_text = "HIGH PRIORITY ISSUES"
    elif medium > 0:
        status_color = "yellow"
        status_text = "WARNINGS"
    else:
        status_color = "green"
        status_text = "ALL CLEAR"
    
    summary = f"""
[bold {status_color}]{status_text}[/bold {status_color}]

[bold]Total Issues:[/bold] {total}
  [red]Critical:[/red] {critical}  [orange1]High:[/orange1] {high}  [yellow]Medium:[/yellow] {medium}  [dim]Low:[/dim] {low}

[dim]Duration:[/dim] {result.get('duration', 0):.2f}s
[dim]Avg Response:[/dim] {result.get('avg_response_time', 0):.0f}ms
[dim]Uptime:[/dim] {result.get('uptime_percentage', 100):.2f}%
"""
    
    if not compact:
        if result.get('report_path'):
            summary += f"\n[dim]Report:[/dim] {result['report_path']}"
    
    console.print(Panel(summary.strip(), title="Check Results", border_style=status_color))


@cli.command()
def init():
    """Initialize configuration for a new website."""
    console.print(Panel.fit(
        "[bold blue]WordPress Monitor Setup[/bold blue]",
        border_style="blue"
    ))
    
    url = click.prompt('Website URL', default='https://example.com')
    email = click.prompt('Alert email', default='')
    
    config_content = f"""# WordPress Monitor Configuration
website:
  url: "{url}"
  name: "My WordPress Site"

alerts:
  email:
    enabled: {str(bool(email)).lower()}
    recipients:
      - "{email}"

critical_pages:
  - "/"
  - "/contact"
  - "/about"

thresholds:
  response_time_warning: 2000
  response_time_critical: 3000
  ssl_expiry_warning: 30
  ssl_expiry_critical: 7
"""
    
    config_path = Path('config/config.yaml')
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, 'w') as f:
        f.write(config_content)
    
    console.print(f"\n[green]Configuration saved to {config_path}[/green]")
    console.print("\nRun [bold]python cli.py check[/bold] to start monitoring!")


if __name__ == '__main__':
    cli()
