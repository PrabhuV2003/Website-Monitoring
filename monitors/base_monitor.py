"""
Base Monitor - Abstract base class for all monitors.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime
import time
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import get_logger

class MonitorResult:
    """Represents a single monitoring result."""
    
    def __init__(self, monitor_type: str, status: str, message: str,
                 severity: str = 'info', url: str = None, 
                 response_time: float = None, details: Dict = None):
        self.monitor_type = monitor_type
        self.status = status  # success, warning, error, critical
        self.message = message
        self.severity = severity  # critical, high, medium, low
        self.url = url
        self.response_time = response_time
        self.details = details or {}
        self.timestamp = datetime.utcnow()
        self.screenshot_path = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'monitor_type': self.monitor_type,
            'status': self.status,
            'message': self.message,
            'severity': self.severity,
            'url': self.url,
            'response_time': self.response_time,
            'details': self.details,
            'timestamp': self.timestamp.isoformat(),
            'screenshot_path': self.screenshot_path
        }

class BaseMonitor(ABC):
    """Abstract base class for all monitors."""
    
    def __init__(self, config: Dict[str, Any], base_url: str):
        self.config = config
        self.base_url = base_url.rstrip('/')
        self.logger = get_logger()
        self.results: List[MonitorResult] = []
        self.cancel_event = config.get('_cancel_event', None)
        self.retry_config = config.get('retry', {
            'max_attempts': 3,
            'initial_delay': 5,
            'exponential_backoff': True,
            'max_delay': 60
        })
    
    def is_cancelled(self) -> bool:
        """Check if the monitor has been cancelled."""
        if self.cancel_event and self.cancel_event.is_set():
            return True
        return False
    
    @abstractmethod
    def run(self) -> List[MonitorResult]:
        """Run the monitor checks. Must be implemented by subclasses."""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return monitor name."""
        pass
    
    def add_result(self, status: str, message: str, severity: str = 'info',
                   url: str = None, response_time: float = None, 
                   details: Dict = None):
        """Add a result to the results list."""
        result = MonitorResult(
            monitor_type=self.name,
            status=status,
            message=message,
            severity=severity,
            url=url,
            response_time=response_time,
            details=details
        )
        self.results.append(result)
        
        # Log based on severity
        if severity in ['critical', 'high']:
            self.logger.error(f"[{self.name}] {message}")
        elif severity == 'medium':
            self.logger.warning(f"[{self.name}] {message}")
        else:
            self.logger.info(f"[{self.name}] {message}")
    
    def retry_with_backoff(self, func, *args, **kwargs):
        """Execute a function with retry and exponential backoff."""
        max_attempts = self.retry_config.get('max_attempts', 3)
        initial_delay = self.retry_config.get('initial_delay', 5)
        exponential = self.retry_config.get('exponential_backoff', True)
        max_delay = self.retry_config.get('max_delay', 60)
        
        last_exception = None
        for attempt in range(max_attempts):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < max_attempts - 1:
                    delay = initial_delay * (2 ** attempt) if exponential else initial_delay
                    delay = min(delay, max_delay)
                    self.logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay}s: {e}")
                    time.sleep(delay)
        
        raise last_exception
    
    def get_full_url(self, path: str) -> str:
        """Get full URL from path."""
        if path.startswith('http'):
            return path
        return f"{self.base_url}{path if path.startswith('/') else '/' + path}"
    
    def get_issues(self) -> List[MonitorResult]:
        """Get all issues (non-success results)."""
        return [r for r in self.results if r.status != 'success']
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the monitor run."""
        return {
            'total_checks': len(self.results),
            'successful': len([r for r in self.results if r.status == 'success']),
            'warnings': len([r for r in self.results if r.status == 'warning']),
            'errors': len([r for r in self.results if r.status == 'error']),
            'critical': len([r for r in self.results if r.status == 'critical'])
        }
