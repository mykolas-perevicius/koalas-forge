"""
🔄 Auto Update Plugin for Koala's Forge
Automatically checks for and notifies about available updates

Installation:
  Copy this file to: ~/.koalas-forge/plugins/auto_update_plugin.py

Features:
  - Check for updates on a schedule
  - Notify when updates are available
  - Track update history
  - Support for auto-updating (if enabled)
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from src.core.event_system import Event, EventType


class AutoUpdatePlugin:
    """Automatically checks for application updates"""

    name = "AutoUpdatePlugin"
    version = "1.0.0"
    description = "Automatic update checking and notifications"

    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.config_file = Path.home() / ".koalas-forge" / "auto_update_config.json"
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        # Load configuration
        self.config = self._load_config()

        # Track update status
        self.available_updates = []
        self.last_check = None

        print(f"🔄 {self.name} v{self.version} initialized")

    def activate(self):
        """Register event handlers"""
        # Listen for system startup
        self.event_bus.on(EventType.SYSTEM_STARTED, self._on_system_started)

        # Listen for installation completion to check if updates available
        self.event_bus.on(EventType.INSTALL_COMPLETED, self._on_install_completed)

        print(f"  ✓ Registered update checker handlers")

        # Do initial update check if enabled
        if self.config.get('check_on_startup', True):
            self._check_for_updates()

    def deactivate(self):
        """Save configuration and cleanup"""
        self._save_config()
        print(f"  ✓ Auto-update configuration saved")

    def _load_config(self) -> Dict:
        """Load plugin configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass

        # Default configuration
        return {
            'enabled': True,
            'check_on_startup': True,
            'check_interval_hours': 24,
            'auto_update': False,  # Don't auto-update by default
            'notify_updates': True,
            'update_history': [],
            'last_check': None,
            'ignored_updates': []  # Apps user wants to skip
        }

    def _save_config(self):
        """Save plugin configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"  ⚠️  Failed to save config: {e}")

    def _on_system_started(self, event: Event):
        """Handle system startup"""
        if self.config.get('check_on_startup', True):
            self._check_for_updates()

    def _on_install_completed(self, event: Event):
        """Handle installation completion"""
        # Mark app as up-to-date
        app = event.data.get('app')
        if app:
            # Remove from available updates if present
            self.available_updates = [
                u for u in self.available_updates if u['app'] != app
            ]

    def _check_for_updates(self):
        """Check for available updates"""
        if not self.config.get('enabled', True):
            return

        # Check if enough time has passed since last check
        last_check = self.config.get('last_check')
        if last_check:
            last_check_time = datetime.fromisoformat(last_check)
            interval = timedelta(hours=self.config.get('check_interval_hours', 24))

            if datetime.now() - last_check_time < interval:
                print(f"  ⏱️  Too soon for update check (last: {last_check_time.strftime('%Y-%m-%d %H:%M')})")
                return

        print(f"  🔍 Checking for updates...")

        # In a real implementation, this would:
        # 1. Query package managers (brew, apt, etc.)
        # 2. Check app versions
        # 3. Compare with installed versions
        # 4. Build list of available updates

        # Mock update check for demonstration
        self.available_updates = self._mock_update_check()

        # Update last check time
        self.config['last_check'] = datetime.now().isoformat()
        self.last_check = datetime.now()
        self._save_config()

        # Notify about updates
        if self.available_updates and self.config.get('notify_updates', True):
            self._notify_updates()

        # Auto-update if enabled
        if self.available_updates and self.config.get('auto_update', False):
            self._auto_update()

    def _mock_update_check(self) -> List[Dict]:
        """Mock update check (replace with real implementation)"""
        # This is a placeholder - real implementation would query package managers
        # For now, return empty list
        return []

        # Example of what this might return:
        # return [
        #     {
        #         'app': 'git',
        #         'current_version': '2.42.0',
        #         'available_version': '2.43.0',
        #         'release_date': '2025-01-01',
        #         'changelog': 'Bug fixes and improvements'
        #     }
        # ]

    def _notify_updates(self):
        """Notify about available updates"""
        count = len(self.available_updates)

        # Emit event for other plugins to handle
        self.event_bus.emit_sync(Event(
            type=EventType.UPDATE_AVAILABLE,
            data={
                'count': count,
                'updates': self.available_updates
            },
            source='auto_update_plugin'
        ))

        # Print notification
        print(f"  🔔 {count} update(s) available!")

        for update in self.available_updates[:5]:  # Show first 5
            app = update['app']
            current = update.get('current_version', 'unknown')
            available = update.get('available_version', 'unknown')
            print(f"     • {app}: {current} → {available}")

        if count > 5:
            print(f"     ... and {count - 5} more")

    def _auto_update(self):
        """Automatically update apps (if enabled)"""
        print(f"  🔄 Auto-updating {len(self.available_updates)} app(s)...")

        for update in self.available_updates:
            app = update['app']

            # Skip if user ignored this update
            if app in self.config.get('ignored_updates', []):
                continue

            # Emit update event
            self.event_bus.emit_sync(Event(
                type=EventType.UPDATE_STARTED,
                data=update,
                source='auto_update_plugin'
            ))

            # In real implementation, would trigger actual update
            print(f"     ⬆️  Updating {app}...")

        # Record update in history
        self.config['update_history'].append({
            'timestamp': datetime.now().isoformat(),
            'count': len(self.available_updates),
            'apps': [u['app'] for u in self.available_updates]
        })

        self._save_config()

    def get_update_report(self) -> str:
        """Generate update status report"""
        report = []
        report.append("\n" + "="*60)
        report.append("🔄 Auto-Update Status")
        report.append("="*60)

        # Configuration
        report.append(f"\nConfiguration:")
        report.append(f"  Enabled: {self.config.get('enabled', True)}")
        report.append(f"  Check on startup: {self.config.get('check_on_startup', True)}")
        report.append(f"  Check interval: {self.config.get('check_interval_hours', 24)} hours")
        report.append(f"  Auto-update: {self.config.get('auto_update', False)}")

        # Last check
        last_check = self.config.get('last_check')
        if last_check:
            last_check_time = datetime.fromisoformat(last_check)
            report.append(f"\nLast check: {last_check_time.strftime('%Y-%m-%d %H:%M')}")

        # Available updates
        if self.available_updates:
            report.append(f"\nAvailable Updates ({len(self.available_updates)}):")
            for update in self.available_updates:
                app = update['app']
                current = update.get('current_version', '?')
                available = update.get('available_version', '?')
                report.append(f"  • {app}: {current} → {available}")
        else:
            report.append(f"\nNo updates available")

        # Update history
        history = self.config.get('update_history', [])
        if history:
            report.append(f"\nRecent Updates:")
            for entry in history[-5:]:
                timestamp = datetime.fromisoformat(entry['timestamp'])
                apps = ', '.join(entry['apps'][:3])
                if len(entry['apps']) > 3:
                    apps += f" +{len(entry['apps'])-3} more"
                report.append(f"  {timestamp.strftime('%Y-%m-%d')}: {apps}")

        report.append("="*60)
        return "\n".join(report)


# Plugin entry point
def create_plugin(event_bus):
    """Factory function to create plugin instance"""
    return AutoUpdatePlugin(event_bus)
