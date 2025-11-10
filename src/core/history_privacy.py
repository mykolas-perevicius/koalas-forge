"""
Enhanced History System with Privacy Controls and Breakage Detection
Provides privacy features, causality tracking, and system state monitoring
"""

import json
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Set
from dataclasses import dataclass, field, asdict


@dataclass
class SystemState:
    """Captures system state at a point in time"""
    timestamp: str
    working_packages: Set[str] = field(default_factory=set)
    broken_packages: Set[str] = field(default_factory=set)
    system_errors: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, float] = field(default_factory=dict)

    def to_dict(self):
        """Convert to dictionary for serialization"""
        return {
            'timestamp': self.timestamp,
            'working_packages': list(self.working_packages),
            'broken_packages': list(self.broken_packages),
            'system_errors': self.system_errors,
            'performance_metrics': self.performance_metrics
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create from dictionary"""
        return cls(
            timestamp=data['timestamp'],
            working_packages=set(data.get('working_packages', [])),
            broken_packages=set(data.get('broken_packages', [])),
            system_errors=data.get('system_errors', []),
            performance_metrics=data.get('performance_metrics', {})
        )


@dataclass
class BreakageEvent:
    """Records when something breaks something else"""
    timestamp: str
    suspected_cause: str  # Package that likely caused the issue
    affected_packages: List[str]  # Packages that stopped working
    error_type: str  # Type of breakage
    confidence: float  # 0.0 to 1.0 confidence in causality
    recovery_action: Optional[str] = None  # Suggested fix

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(**data)


class PrivacyConfig:
    """Privacy configuration for history tracking"""

    def __init__(self):
        self.config_file = Path.home() / '.koalas-forge' / 'privacy.json'
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load privacy configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                pass

        # Default privacy settings
        return {
            'tracking_enabled': True,
            'anonymize_packages': False,
            'auto_clear_days': 90,  # Auto-clear history older than X days
            'track_system_state': True,
            'track_performance': True,
            'share_analytics': False,
            'detailed_errors': True
        }

    def save_config(self):
        """Save privacy configuration"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def set(self, key: str, value: Any):
        """Set a privacy configuration value"""
        self.config[key] = value
        self.save_config()

    def get(self, key: str, default: Any = None) -> Any:
        """Get a privacy configuration value"""
        return self.config.get(key, default)


class EnhancedHistory:
    """Enhanced history with privacy and breakage detection"""

    def __init__(self):
        self.history_dir = Path.home() / '.koalas-forge' / 'history'
        self.history_file = self.history_dir / 'enhanced_history.json'
        self.state_file = self.history_dir / 'system_states.json'
        self.breakage_file = self.history_dir / 'breakage_events.json'
        self.privacy = PrivacyConfig()

        self._ensure_dirs()
        self._states: List[SystemState] = self._load_states()
        self._breakages: List[BreakageEvent] = self._load_breakages()
        self._apply_privacy_policies()

    def _ensure_dirs(self):
        """Ensure history directories exist"""
        self.history_dir.mkdir(parents=True, exist_ok=True)

    def _load_states(self) -> List[SystemState]:
        """Load system states from file"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    return [SystemState.from_dict(s) for s in data.get('states', [])]
            except:
                pass
        return []

    def _load_breakages(self) -> List[BreakageEvent]:
        """Load breakage events from file"""
        if self.breakage_file.exists():
            try:
                with open(self.breakage_file, 'r') as f:
                    data = json.load(f)
                    return [BreakageEvent.from_dict(b) for b in data.get('breakages', [])]
            except:
                pass
        return []

    def _save_states(self):
        """Save system states to file"""
        data = {
            'version': '1.0',
            'last_updated': datetime.now().isoformat(),
            'states': [s.to_dict() for s in self._states]
        }
        with open(self.state_file, 'w') as f:
            json.dump(data, f, indent=2)

    def _save_breakages(self):
        """Save breakage events to file"""
        data = {
            'version': '1.0',
            'last_updated': datetime.now().isoformat(),
            'breakages': [b.to_dict() for b in self._breakages]
        }
        with open(self.breakage_file, 'w') as f:
            json.dump(data, f, indent=2)

    def _apply_privacy_policies(self):
        """Apply privacy policies like auto-clearing old data"""
        if not self.privacy.get('tracking_enabled'):
            return

        auto_clear_days = self.privacy.get('auto_clear_days')
        if auto_clear_days and auto_clear_days > 0:
            cutoff_date = datetime.now() - timedelta(days=auto_clear_days)

            # Clear old states
            self._states = [
                s for s in self._states
                if datetime.fromisoformat(s.timestamp) > cutoff_date
            ]

            # Clear old breakages
            self._breakages = [
                b for b in self._breakages
                if datetime.fromisoformat(b.timestamp) > cutoff_date
            ]

            self._save_states()
            self._save_breakages()

    def anonymize_package_name(self, package: str) -> str:
        """Anonymize package name for privacy"""
        if self.privacy.get('anonymize_packages'):
            # Create a hash of the package name
            hash_obj = hashlib.sha256(package.encode())
            return f"pkg_{hash_obj.hexdigest()[:8]}"
        return package

    def capture_system_state(self) -> SystemState:
        """Capture current system state"""
        if not self.privacy.get('track_system_state'):
            return SystemState(timestamp=datetime.now().isoformat())

        state = SystemState(timestamp=datetime.now().isoformat())

        # Check which packages are working (simplified - would need real checks)
        try:
            # Example: Check if common tools respond
            test_commands = {
                'git': ['git', '--version'],
                'docker': ['docker', '--version'],
                'python': ['python3', '--version'],
                'node': ['node', '--version']
            }

            for pkg, cmd in test_commands.items():
                try:
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        timeout=2,
                        text=True
                    )
                    if result.returncode == 0:
                        state.working_packages.add(pkg)
                    else:
                        state.broken_packages.add(pkg)
                except:
                    state.broken_packages.add(pkg)
        except:
            pass

        # Capture performance metrics if enabled
        if self.privacy.get('track_performance'):
            try:
                import psutil
                state.performance_metrics = {
                    'cpu_percent': psutil.cpu_percent(interval=1),
                    'memory_percent': psutil.virtual_memory().percent,
                    'disk_usage': psutil.disk_usage('/').percent
                }
            except:
                pass

        return state

    def detect_breakage(self, before_state: SystemState, after_state: SystemState,
                       action_package: str, action: str) -> Optional[BreakageEvent]:
        """Detect if an action caused breakage"""
        # Find packages that were working before but not after
        newly_broken = before_state.working_packages - after_state.working_packages

        if newly_broken:
            # Calculate confidence based on timing and correlation
            confidence = 0.9 if len(newly_broken) <= 2 else 0.7

            # Suggest recovery action
            recovery = None
            if action == 'install':
                recovery = f"uninstall {action_package}"
            elif action == 'update':
                recovery = f"rollback {action_package}"

            breakage = BreakageEvent(
                timestamp=datetime.now().isoformat(),
                suspected_cause=action_package,
                affected_packages=list(newly_broken),
                error_type=f"{action}_induced_failure",
                confidence=confidence,
                recovery_action=recovery
            )

            return breakage

        return None

    def record_action_with_state(self, package: str, action: str, success: bool,
                                 details: Dict[str, Any] = None) -> Optional[BreakageEvent]:
        """Record an action and detect any breakages it caused"""
        if not self.privacy.get('tracking_enabled'):
            return None

        # Capture state before action
        before_state = self.capture_system_state()

        # Record the action (would integrate with existing history)
        # ... existing history recording ...

        # Capture state after action
        import time
        time.sleep(2)  # Give system time to stabilize
        after_state = self.capture_system_state()

        # Save states
        self._states.append(before_state)
        self._states.append(after_state)
        self._save_states()

        # Detect breakages
        breakage = self.detect_breakage(before_state, after_state, package, action)
        if breakage:
            self._breakages.append(breakage)
            self._save_breakages()
            return breakage

        return None

    def get_breakages_by_package(self, package: str) -> List[BreakageEvent]:
        """Get all breakages caused by a specific package"""
        return [
            b for b in self._breakages
            if b.suspected_cause == package
        ]

    def get_recent_breakages(self, days: int = 7) -> List[BreakageEvent]:
        """Get recent breakage events"""
        cutoff_date = datetime.now() - timedelta(days=days)
        return [
            b for b in self._breakages
            if datetime.fromisoformat(b.timestamp) > cutoff_date
        ]

    def clear_all_history(self, confirm: bool = False):
        """Clear all history data (privacy feature)"""
        if not confirm:
            raise ValueError("Must confirm history clearing")

        # Clear all data
        self._states = []
        self._breakages = []

        # Delete files
        for file in [self.history_file, self.state_file, self.breakage_file]:
            if file.exists():
                file.unlink()

        print("✅ All history data has been cleared")

    def export_anonymized(self, output_file: str):
        """Export anonymized history for sharing"""
        data = {
            'exported_at': datetime.now().isoformat(),
            'anonymized': True,
            'states_count': len(self._states),
            'breakages_count': len(self._breakages),
            'breakage_summary': []
        }

        # Add anonymized breakage summary
        for b in self._breakages:
            summary = {
                'timestamp': b.timestamp,
                'suspected_cause': self.anonymize_package_name(b.suspected_cause),
                'affected_count': len(b.affected_packages),
                'error_type': b.error_type,
                'confidence': b.confidence
            }
            data['breakage_summary'].append(summary)

        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"✅ Anonymized history exported to {output_file}")

    def get_privacy_report(self) -> Dict[str, Any]:
        """Generate a privacy report"""
        return {
            'tracking_enabled': self.privacy.get('tracking_enabled'),
            'anonymization': self.privacy.get('anonymize_packages'),
            'auto_clear_days': self.privacy.get('auto_clear_days'),
            'data_collected': {
                'system_states': len(self._states),
                'breakage_events': len(self._breakages),
                'oldest_entry': self._states[0].timestamp if self._states else None,
                'storage_size_kb': sum(
                    f.stat().st_size / 1024
                    for f in [self.history_file, self.state_file, self.breakage_file]
                    if f.exists()
                )
            },
            'privacy_settings': self.privacy.config
        }


# Singleton instance
_enhanced_history_instance: Optional[EnhancedHistory] = None


def get_enhanced_history() -> EnhancedHistory:
    """Get the singleton enhanced history instance"""
    global _enhanced_history_instance
    if _enhanced_history_instance is None:
        _enhanced_history_instance = EnhancedHistory()
    return _enhanced_history_instance