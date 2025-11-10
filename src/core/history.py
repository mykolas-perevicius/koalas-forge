"""
Installation History Tracker for Koala's Forge
Tracks all package installation, update, and uninstall operations
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any


class HistoryEntry:
    """Represents a single history entry"""

    def __init__(self,
                 package: str,
                 action: str,
                 timestamp: str = None,
                 success: bool = True,
                 details: Dict[str, Any] = None):
        self.package = package
        self.action = action  # install, update, uninstall
        self.timestamp = timestamp or datetime.now().isoformat()
        self.success = success
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'package': self.package,
            'action': self.action,
            'timestamp': self.timestamp,
            'success': self.success,
            'details': self.details
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'HistoryEntry':
        """Create from dictionary"""
        return HistoryEntry(
            package=data['package'],
            action=data['action'],
            timestamp=data.get('timestamp'),
            success=data.get('success', True),
            details=data.get('details', {})
        )


class InstallHistory:
    """Manages installation history"""

    def __init__(self):
        self.history_dir = Path.home() / '.koalas-forge' / 'history'
        self.history_file = self.history_dir / 'install_history.json'
        self._ensure_history_dir()
        self._entries: List[HistoryEntry] = []
        self._load_history()

    def _ensure_history_dir(self):
        """Ensure history directory exists"""
        self.history_dir.mkdir(parents=True, exist_ok=True)

    def _load_history(self):
        """Load history from file"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    self._entries = [
                        HistoryEntry.from_dict(entry)
                        for entry in data.get('entries', [])
                    ]
            except Exception as e:
                print(f"Warning: Could not load history: {e}")
                self._entries = []
        else:
            self._entries = []

    def _save_history(self):
        """Save history to file"""
        try:
            data = {
                'version': '1.0',
                'last_updated': datetime.now().isoformat(),
                'entries': [entry.to_dict() for entry in self._entries]
            }

            with open(self.history_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save history: {e}")

    def add_entry(self,
                  package: str,
                  action: str,
                  success: bool = True,
                  details: Dict[str, Any] = None):
        """Add a new history entry"""
        entry = HistoryEntry(
            package=package,
            action=action,
            success=success,
            details=details
        )
        self._entries.append(entry)
        self._save_history()

    def get_all_entries(self, limit: Optional[int] = None) -> List[HistoryEntry]:
        """Get all history entries (newest first)"""
        entries = sorted(self._entries,
                        key=lambda x: x.timestamp,
                        reverse=True)
        if limit:
            return entries[:limit]
        return entries

    def get_entries_for_package(self, package: str) -> List[HistoryEntry]:
        """Get history entries for a specific package"""
        return [
            entry for entry in self._entries
            if entry.package.lower() == package.lower()
        ]

    def get_entries_by_action(self, action: str) -> List[HistoryEntry]:
        """Get entries by action type"""
        return [
            entry for entry in self._entries
            if entry.action == action
        ]

    def get_entries_by_date(self,
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None) -> List[HistoryEntry]:
        """Get entries within a date range"""
        entries = self._entries

        if start_date:
            entries = [
                e for e in entries
                if datetime.fromisoformat(e.timestamp) >= start_date
            ]

        if end_date:
            entries = [
                e for e in entries
                if datetime.fromisoformat(e.timestamp) <= end_date
            ]

        return sorted(entries, key=lambda x: x.timestamp, reverse=True)

    def get_failed_entries(self) -> List[HistoryEntry]:
        """Get all failed installations"""
        return [
            entry for entry in self._entries
            if not entry.success
        ]

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about installation history"""
        total = len(self._entries)

        if total == 0:
            return {
                'total': 0,
                'installs': 0,
                'updates': 0,
                'uninstalls': 0,
                'success_rate': 0.0,
                'unique_packages': 0
            }

        installs = len([e for e in self._entries if e.action == 'install'])
        updates = len([e for e in self._entries if e.action == 'update'])
        uninstalls = len([e for e in self._entries if e.action == 'uninstall'])
        successes = len([e for e in self._entries if e.success])

        unique_packages = len(set(e.package for e in self._entries))

        return {
            'total': total,
            'installs': installs,
            'updates': updates,
            'uninstalls': uninstalls,
            'success_rate': (successes / total) * 100,
            'unique_packages': unique_packages
        }

    def get_last_action(self, package: str) -> Optional[HistoryEntry]:
        """Get the last action performed on a package"""
        package_entries = self.get_entries_for_package(package)
        if package_entries:
            return sorted(package_entries,
                         key=lambda x: x.timestamp,
                         reverse=True)[0]
        return None

    def clear_history(self):
        """Clear all history (use with caution)"""
        self._entries = []
        self._save_history()

    def export_history(self, output_file: str, format: str = 'json'):
        """Export history to a file"""
        entries = self.get_all_entries()

        if format == 'json':
            data = {
                'exported_at': datetime.now().isoformat(),
                'total_entries': len(entries),
                'entries': [e.to_dict() for e in entries]
            }

            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)

        elif format == 'txt':
            with open(output_file, 'w') as f:
                f.write(f"Koala's Forge Installation History\n")
                f.write(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total entries: {len(entries)}\n\n")
                f.write("="*80 + "\n\n")

                for entry in entries:
                    timestamp = datetime.fromisoformat(entry.timestamp)
                    status = "✅" if entry.success else "❌"
                    f.write(f"{timestamp.strftime('%Y-%m-%d %H:%M:%S')} | {status} | {entry.action.upper():<10} | {entry.package}\n")

                    if entry.details:
                        for key, value in entry.details.items():
                            f.write(f"  {key}: {value}\n")
                    f.write("\n")


# Singleton instance
_history_instance: Optional[InstallHistory] = None


def get_history() -> InstallHistory:
    """Get the singleton history instance"""
    global _history_instance
    if _history_instance is None:
        _history_instance = InstallHistory()
    return _history_instance
