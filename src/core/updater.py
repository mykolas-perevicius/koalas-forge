"""
Auto-update checker for Koala's Forge
Checks GitHub for new releases
"""

import requests
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any


class UpdateChecker:
    """
    Checks for Koala's Forge updates from GitHub
    """

    def __init__(self, current_version: str):
        self.current_version = current_version
        self.cache_dir = Path.home() / '.koalas-forge' / 'cache'
        self.cache_file = self.cache_dir / 'update_check.json'
        self.github_api = "https://api.github.com/repos/mykolas-perevicius/koalas-forge/releases/latest"

    def _load_cache(self) -> Optional[Dict[str, Any]]:
        """Load cached update check"""
        if not self.cache_file.exists():
            return None

        try:
            with open(self.cache_file, 'r') as f:
                cache = json.load(f)

            # Check if cache is less than 24 hours old
            cached_time = datetime.fromisoformat(cache['timestamp'])
            if datetime.now() - cached_time < timedelta(hours=24):
                return cache

        except Exception:
            pass

        return None

    def _save_cache(self, data: Dict[str, Any]) -> None:
        """Save update check to cache"""
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

            cache_data = {
                'timestamp': datetime.now().isoformat(),
                **data
            }

            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f)

        except Exception:
            pass  # Fail silently if we can't cache

    def check_for_updates(self, silent: bool = False) -> Optional[Dict[str, Any]]:
        """
        Check if a new version is available

        Returns dict with:
        - update_available: bool
        - latest_version: str
        - release_url: str
        - release_notes: str
        """
        # Check cache first
        cached = self._load_cache()
        if cached and silent:
            return cached

        try:
            response = requests.get(self.github_api, timeout=3)

            if response.status_code != 200:
                return None

            release_data = response.json()

            latest_version = release_data.get('tag_name', '').lstrip('v')
            if not latest_version:
                latest_version = release_data.get('name', '').lstrip('v')

            result = {
                'update_available': self._is_newer_version(latest_version),
                'latest_version': latest_version,
                'current_version': self.current_version,
                'release_url': release_data.get('html_url', ''),
                'release_notes': release_data.get('body', '')[:500],  # First 500 chars
                'published_at': release_data.get('published_at', ''),
            }

            self._save_cache(result)
            return result

        except Exception:
            # Fail silently for network errors
            return cached if cached else None

    def _is_newer_version(self, latest: str) -> bool:
        """Compare version strings"""
        try:
            current_parts = [int(x) for x in self.current_version.split('.')]
            latest_parts = [int(x) for x in latest.split('.')]

            # Pad to same length
            max_len = max(len(current_parts), len(latest_parts))
            current_parts.extend([0] * (max_len - len(current_parts)))
            latest_parts.extend([0] * (max_len - len(latest_parts)))

            return latest_parts > current_parts

        except Exception:
            return False

    def notify_if_update_available(self) -> None:
        """Print notification if update is available"""
        update_info = self.check_for_updates(silent=True)

        if not update_info or not update_info.get('update_available'):
            return

        print(f"\n{'='*60}")
        print(f"📦 Update Available!")
        print(f"   Current: v{update_info['current_version']}")
        print(f"   Latest:  v{update_info['latest_version']}")
        print(f"\n   Update: git pull")
        print(f"   Release: {update_info['release_url']}")
        print(f"{'='*60}\n")


def get_update_checker(version: str) -> UpdateChecker:
    """Get global update checker instance"""
    return UpdateChecker(version)
