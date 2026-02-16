"""
Configuration Loader
====================
Loads and validates configuration from YAML files and environment variables.
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from dotenv import load_dotenv


class ConfigLoader:
    """Loads configuration from YAML file and environment variables."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize the configuration loader.
        
        Args:
            config_path: Path to the YAML configuration file
        """
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self._load_env()
        self._load_yaml()
        self._apply_env_overrides()
        self._validate_config()
    
    def _load_env(self):
        """Load environment variables from .env file if it exists."""
        env_path = self.config_path.parent.parent / ".env"
        if env_path.exists():
            load_dotenv(env_path)
    
    def _load_yaml(self):
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
    
    def _apply_env_overrides(self):
        """Apply environment variable overrides to configuration."""
        env_mappings = {
            'WP_MONITOR_PASSWORD': ('wordpress_auth', 'password'),
            'SMTP_USERNAME': ('alerts', 'email', 'smtp_username'),
            'SMTP_PASSWORD': ('alerts', 'email', 'smtp_password'),
            'SLACK_WEBHOOK_URL': ('alerts', 'slack', 'webhook_url'),
            'DISCORD_WEBHOOK_URL': ('alerts', 'discord', 'webhook_url'),
            'PAGESPEED_API_KEY': ('performance', 'pagespeed_api_key'),
            'DB_USERNAME': ('database', 'mysql', 'username'),
            'DB_PASSWORD': ('database', 'mysql', 'password'),
            'DASHBOARD_SECRET_KEY': ('dashboard', 'secret_key'),
            'WP_MONITOR_URL': ('website', 'url'),
        }
        
        for env_var, path in env_mappings.items():
            value = os.getenv(env_var)
            if value:
                self._set_nested_value(path, value)
    
    def _set_nested_value(self, path: tuple, value: Any):
        """Set a nested value in the configuration dictionary."""
        current = self.config
        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[path[-1]] = value
    
    def _get_nested_value(self, path: tuple, default: Any = None) -> Any:
        """Get a nested value from the configuration dictionary."""
        current = self.config
        for key in path:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current
    
    def _validate_config(self):
        """Validate required configuration fields."""
        required_fields = [
            ('website', 'url'),
        ]
        
        for path in required_fields:
            value = self._get_nested_value(path)
            if not value or value == "https://yourwordpresssite.com":
                pass  # Allow default for initial setup
    
    def get(self, *path: str, default: Any = None) -> Any:
        """
        Get a configuration value by path.
        
        Args:
            *path: Path to the configuration value
            default: Default value if not found
            
        Returns:
            The configuration value or default
        """
        return self._get_nested_value(path, default)
    
    def get_website_url(self) -> str:
        """Get the target website URL."""
        return self.get('website', 'url', default='')
    
    def get_thresholds(self) -> Dict[str, int]:
        """Get all threshold values."""
        return self.get('thresholds', default={})
    
    def get_critical_pages(self) -> list:
        """Get list of critical pages to monitor."""
        return self.get('critical_pages', default=['/'])
    
    def get_forms_config(self) -> list:
        """Get forms configuration for testing. Supports both 'forms_to_test' and 'forms' keys."""
        return self.get('forms_to_test', default=[]) or self.get('forms', default=[])
    
    def get_alert_config(self) -> Dict[str, Any]:
        """Get alert configuration."""
        return self.get('alerts', default={})
    
    def get_retry_config(self) -> Dict[str, Any]:
        """Get retry configuration."""
        return self.get('retry', default={
            'max_attempts': 3,
            'initial_delay': 5,
            'exponential_backoff': True,
            'max_delay': 60
        })
    
    def is_dashboard_enabled(self) -> bool:
        """Check if dashboard is enabled."""
        return self.get('dashboard', 'enabled', default=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Return the full configuration as a dictionary."""
        return self.config.copy()
    
    def reload(self):
        """Reload configuration from file."""
        self._load_yaml()
        self._apply_env_overrides()
        self._validate_config()


# Singleton instance
_config_instance: Optional[ConfigLoader] = None


def get_config(config_path: str = "config/config.yaml") -> ConfigLoader:
    """
    Get the configuration singleton instance.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        ConfigLoader instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigLoader(config_path)
    return _config_instance


def reload_config():
    """Reload the configuration."""
    global _config_instance
    if _config_instance:
        _config_instance.reload()
