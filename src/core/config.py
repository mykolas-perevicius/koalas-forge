"""
Configuration management for Koala's Forge
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class Config:
    """
    Manages user configuration from ~/.koalas-forge/config.yaml

    Default configuration:
    - parallel_install: false
    - auto_rollback: true
    - cloud_sync_enabled: true
    - event_history_limit: 100
    - plugin_auto_load: true
    """

    DEFAULT_CONFIG = {
        'parallel_install': False,
        'auto_rollback': True,
        'cloud_sync_enabled': True,
        'event_history_limit': 100,
        'plugin_auto_load': True,
        'confirm_before_install': True,
        'dry_run_by_default': False,
    }

    def __init__(self):
        self.config_dir = Path.home() / '.koalas-forge'
        self.config_file = self.config_dir / 'config.yaml'
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if not self.config_file.exists():
            return self.DEFAULT_CONFIG.copy()

        try:
            with open(self.config_file, 'r') as f:
                user_config = yaml.safe_load(f) or {}

            # Merge with defaults
            config = self.DEFAULT_CONFIG.copy()
            config.update(user_config)
            return config
        except Exception as e:
            print(f"⚠️  Warning: Failed to load config: {e}")
            return self.DEFAULT_CONFIG.copy()

    def save_config(self) -> bool:
        """Save current configuration to file"""
        try:
            # Create directory if it doesn't exist
            self.config_dir.mkdir(parents=True, exist_ok=True)

            with open(self.config_file, 'w') as f:
                yaml.dump(self._config, f, default_flow_style=False, sort_keys=False)

            return True
        except Exception as e:
            print(f"❌ Failed to save config: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        self._config[key] = value

    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults"""
        self._config = self.DEFAULT_CONFIG.copy()

    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values"""
        return self._config.copy()

    def create_default_config_file(self) -> bool:
        """Create default configuration file with comments"""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)

            config_content = """# Koala's Forge Configuration
# This file is automatically created with default values
# Edit as needed

# Install packages concurrently (faster but may be less stable)
parallel_install: false

# Automatically create rollback points before installations
auto_rollback: true

# Enable cloud synchronization
cloud_sync_enabled: true

# Maximum number of events to keep in history
event_history_limit: 100

# Automatically load plugins from ~/.koalas-forge/plugins/
plugin_auto_load: true

# Ask for confirmation before installing packages
confirm_before_install: true

# Use dry-run mode by default (safer, but requires --no-dry-run to actually install)
dry_run_by_default: false
"""

            with open(self.config_file, 'w') as f:
                f.write(config_content)

            return True
        except Exception as e:
            print(f"❌ Failed to create config file: {e}")
            return False


# Global config instance
_config_instance: Optional[Config] = None


def get_config() -> Config:
    """Get global config instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance
