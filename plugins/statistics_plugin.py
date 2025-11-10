"""
📊 Statistics Plugin for Koala's Forge
Tracks installation statistics and generates reports

Installation:
  Copy this file to: ~/.koalas-forge/plugins/statistics_plugin.py

Features:
  - Count installations per app
  - Track success/failure rates
  - Measure installation times
  - Generate statistics reports
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, Any
from src.core.event_system import Event, EventType


class StatisticsPlugin:
    """Tracks and reports installation statistics"""

    name = "StatisticsPlugin"
    version = "1.0.0"
    description = "Track installation statistics and generate reports"

    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.stats_file = Path.home() / ".koalas-forge" / "stats.json"
        self.stats_file.parent.mkdir(parents=True, exist_ok=True)

        # Load existing stats
        self.stats = self._load_stats()

        # Track ongoing installations
        self.active_installs = {}

        print(f"📊 {self.name} v{self.version} initialized")

    def activate(self):
        """Register event handlers"""
        self.event_bus.on(EventType.INSTALL_STARTED, self._on_install_started)
        self.event_bus.on(EventType.INSTALL_COMPLETED, self._on_install_completed)
        self.event_bus.on(EventType.INSTALL_FAILED, self._on_install_failed)
        self.event_bus.on(EventType.DOWNLOAD_STARTED, self._on_download_started)
        self.event_bus.on(EventType.DOWNLOAD_COMPLETED, self._on_download_completed)

        print(f"  ✓ Registered statistics handlers")

    def deactivate(self):
        """Save stats and cleanup"""
        self._save_stats()
        print(f"  ✓ Statistics saved")

    def _load_stats(self) -> Dict[str, Any]:
        """Load statistics from file"""
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass

        # Initialize empty stats
        return {
            'total_installs': 0,
            'successful_installs': 0,
            'failed_installs': 0,
            'apps': defaultdict(lambda: {
                'installs': 0,
                'successes': 0,
                'failures': 0,
                'total_time': 0.0,
                'avg_time': 0.0,
                'last_installed': None
            }),
            'downloads': {
                'total': 0,
                'total_bytes': 0,
                'avg_speed': 0.0
            }
        }

    def _save_stats(self):
        """Save statistics to file"""
        try:
            # Convert defaultdict to regular dict for JSON serialization
            stats_dict = dict(self.stats)
            stats_dict['apps'] = dict(stats_dict['apps'])

            with open(self.stats_file, 'w') as f:
                json.dump(stats_dict, f, indent=2)
        except Exception as e:
            print(f"  ⚠️  Failed to save stats: {e}")

    def _on_install_started(self, event: Event):
        """Track installation start"""
        app = event.data.get('app')
        if app:
            self.active_installs[app] = {
                'start_time': datetime.now(),
                'event': event
            }
            self.stats['total_installs'] += 1

    def _on_install_completed(self, event: Event):
        """Track installation completion"""
        app = event.data.get('app')
        if app and app in self.active_installs:
            # Calculate duration
            start = self.active_installs[app]['start_time']
            duration = (datetime.now() - start).total_seconds()

            # Update app stats
            app_stats = self.stats['apps'][app]
            app_stats['installs'] += 1
            app_stats['successes'] += 1
            app_stats['total_time'] += duration
            app_stats['avg_time'] = app_stats['total_time'] / app_stats['installs']
            app_stats['last_installed'] = datetime.now().isoformat()

            # Update global stats
            self.stats['successful_installs'] += 1

            # Cleanup
            del self.active_installs[app]

            # Save stats
            self._save_stats()

            print(f"  📊 {app} installed in {duration:.1f}s (avg: {app_stats['avg_time']:.1f}s)")

    def _on_install_failed(self, event: Event):
        """Track installation failure"""
        app = event.data.get('app')
        if app:
            # Update app stats
            app_stats = self.stats['apps'][app]
            app_stats['installs'] += 1
            app_stats['failures'] += 1

            # Update global stats
            self.stats['failed_installs'] += 1

            # Cleanup if was tracking
            if app in self.active_installs:
                del self.active_installs[app]

            # Save stats
            self._save_stats()

    def _on_download_started(self, event: Event):
        """Track download start"""
        pass  # Could track download starts

    def _on_download_completed(self, event: Event):
        """Track download completion"""
        size = event.data.get('size', 0)
        if isinstance(size, (int, float)):
            self.stats['downloads']['total'] += 1
            self.stats['downloads']['total_bytes'] += size
            self._save_stats()

    def get_report(self) -> str:
        """Generate statistics report"""
        report = []
        report.append("\n" + "="*60)
        report.append("📊 Koala's Forge - Installation Statistics")
        report.append("="*60)

        # Global stats
        total = self.stats['total_installs']
        success = self.stats['successful_installs']
        failed = self.stats['failed_installs']
        success_rate = (success / total * 100) if total > 0 else 0

        report.append(f"\nGlobal Statistics:")
        report.append(f"  Total installations: {total}")
        report.append(f"  Successful: {success}")
        report.append(f"  Failed: {failed}")
        report.append(f"  Success rate: {success_rate:.1f}%")

        # Top apps
        if self.stats['apps']:
            report.append(f"\nMost Installed Apps:")
            sorted_apps = sorted(
                self.stats['apps'].items(),
                key=lambda x: x[1]['installs'],
                reverse=True
            )[:5]

            for app, stats in sorted_apps:
                report.append(f"  {app}: {stats['installs']} installs, {stats['avg_time']:.1f}s avg")

        # Download stats
        downloads = self.stats['downloads']
        if downloads['total'] > 0:
            total_gb = downloads['total_bytes'] / (1024**3)
            report.append(f"\nDownload Statistics:")
            report.append(f"  Total downloads: {downloads['total']}")
            report.append(f"  Total data: {total_gb:.2f} GB")

        report.append("="*60)
        return "\n".join(report)


# Plugin entry point
def create_plugin(event_bus):
    """Factory function to create plugin instance"""
    return StatisticsPlugin(event_bus)
