"""
Logger Setup
=============
Configures logging for the WordPress Monitor application.
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional
from datetime import datetime


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color support for console output."""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        log_message = super().format(record)
        color = self.COLORS.get(record.levelname, self.RESET)
        return f"{color}{log_message}{self.RESET}"


def setup_logger(
    name: str = "wordpress_monitor",
    log_file: Optional[str] = None,
    level: str = "INFO",
    max_size: int = 10485760,  # 10 MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Set up and configure the logger.
    
    Args:
        name: Logger name
        log_file: Path to the log file
        level: Logging level
        max_size: Maximum log file size in bytes
        backup_count: Number of backup files to keep
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_format = ColoredFormatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=max_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
    
    return logger


class MonitorLogger:
    """Wrapper class for logging with additional context."""
    
    def __init__(self, name: str, log_file: Optional[str] = None):
        self.logger = setup_logger(name, log_file)
        self.check_id: Optional[str] = None
    
    def set_check_id(self, check_id: str):
        """Set the current check ID for context."""
        self.check_id = check_id
    
    def _format_message(self, message: str) -> str:
        """Format message with check ID if available."""
        if self.check_id:
            return f"[{self.check_id}] {message}"
        return message
    
    def debug(self, message: str, **kwargs):
        self.logger.debug(self._format_message(message), **kwargs)
    
    def info(self, message: str, **kwargs):
        self.logger.info(self._format_message(message), **kwargs)
    
    def warning(self, message: str, **kwargs):
        self.logger.warning(self._format_message(message), **kwargs)
    
    def error(self, message: str, **kwargs):
        self.logger.error(self._format_message(message), **kwargs)
    
    def critical(self, message: str, **kwargs):
        self.logger.critical(self._format_message(message), **kwargs)
    
    def exception(self, message: str, **kwargs):
        self.logger.exception(self._format_message(message), **kwargs)


# Global logger instance
_logger: Optional[MonitorLogger] = None


def get_logger() -> MonitorLogger:
    """Get the global logger instance."""
    global _logger
    if _logger is None:
        _logger = MonitorLogger("wordpress_monitor", "logs/monitor.log")
    return _logger
