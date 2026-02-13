"""
Load environment variables from .env file
This should be imported at the top of scheduler.py and other scripts
"""
import os
from pathlib import Path

def load_env():
    """Load environment variables from .env file."""
    env_file = Path(__file__).parent / '.env'
    
    if not env_file.exists():
        print(f"Warning: .env file not found at {env_file}")
        print("SMTP credentials will need to be set manually or configured in config.yaml")
        return False
    
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Parse KEY=VALUE
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Only set if not already set in environment
                if key and value and not os.getenv(key):
                    os.environ[key] = value
    
    return True

# Auto-load when imported
if __name__ != '__main__':
    load_env()
