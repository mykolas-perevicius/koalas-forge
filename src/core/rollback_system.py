#!/usr/bin/env python3
"""
Lightweight Rollback System for Koala's Forge
Tracks installations and enables quick rollback without storing entire files
"""

import asyncio
import json
import logging
import platform
import subprocess
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Any

from .event_system import EventBus, Event, EventType, get_event_bus

logger = logging.getLogger(__name__)


@dataclass
class AppSnapshot:
    """Lightweight snapshot of an installed app"""
    name: str
    package_id: str
    version: str
    install_method: str  # brew, cask, apt, winget, etc.
    install_time: float
    dependencies: List[str] = field(default_factory=list)


@dataclass
class SystemSnapshot:
    """Snapshot of system state at a point in time"""
    id: str
    timestamp: float
    description: str
    installed_apps: List[AppSnapshot] = field(default_factory=list)
    environment_vars: Dict[str, str] = field(default_factory=dict)
    path_entries: List[str] = field(default_factory=list)
    platform_info: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'timestamp': self.timestamp,
            'description': self.description,
            'installed_apps': [asdict(app) for app in self.installed_apps],
            'environment_vars': self.environment_vars,
            'path_entries': self.path_entries,
            'platform_info': self.platform_info
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SystemSnapshot':
        """Create from dictionary"""
        data['installed_apps'] = [
            AppSnapshot(**app) for app in data.get('installed_apps', [])
        ]
        return cls(**data)


class RollbackManager:
    """
    Manages system snapshots and rollback operations
    Uses lightweight package manager references instead of file copies
    """

    def __init__(self, event_bus: Optional[EventBus] = None):
        self.event_bus = event_bus or get_event_bus()
        self.data_dir = Path.home() / ".koalas-forge" / "rollback"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.snapshots_file = self.data_dir / "snapshots.json"
        self.snapshots: Dict[str, SystemSnapshot] = {}
        self._load_snapshots()
        logger.info(f"💾 Rollback data directory: {self.data_dir}")

    def _load_snapshots(self):
        """Load snapshots from disk"""
        if self.snapshots_file.exists():
            try:
                with open(self.snapshots_file, 'r') as f:
                    data = json.load(f)
                    self.snapshots = {
                        snap_id: SystemSnapshot.from_dict(snap_data)
                        for snap_id, snap_data in data.items()
                    }
                logger.info(f"Loaded {len(self.snapshots)} snapshot(s)")
            except Exception as e:
                logger.error(f"Failed to load snapshots: {e}")
                self.snapshots = {}

    def _save_snapshots(self):
        """Save snapshots to disk"""
        try:
            with open(self.snapshots_file, 'w') as f:
                data = {
                    snap_id: snapshot.to_dict()
                    for snap_id, snapshot in self.snapshots.items()
                }
                json.dump(data, f, indent=2)
            logger.debug("Snapshots saved to disk")
        except Exception as e:
            logger.error(f"Failed to save snapshots: {e}")

    async def create_snapshot(self, description: str) -> str:
        """
        Create a lightweight snapshot of current system state

        Args:
            description: Human-readable description of snapshot

        Returns:
            Snapshot ID
        """
        snapshot_id = f"snapshot_{int(time.time())}"

        logger.info(f"📸 Creating snapshot: {description}")

        # Get current system state
        installed_apps = await self._get_installed_apps()
        env_vars = dict(os.environ) if 'os' in dir() else {}
        path_entries = env_vars.get('PATH', '').split(':')

        # Create snapshot
        snapshot = SystemSnapshot(
            id=snapshot_id,
            timestamp=time.time(),
            description=description,
            installed_apps=installed_apps,
            environment_vars=env_vars,
            path_entries=path_entries,
            platform_info={
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine()
            }
        )

        # Store snapshot
        self.snapshots[snapshot_id] = snapshot
        self._save_snapshots()

        # Emit event
        await self.event_bus.emit(Event(
            type=EventType.SNAPSHOT_CREATED,
            data={
                'snapshot_id': snapshot_id,
                'description': description,
                'app_count': len(installed_apps)
            },
            source='rollback_manager'
        ))

        logger.info(f"✅ Snapshot created: {snapshot_id} ({len(installed_apps)} apps)")
        return snapshot_id

    async def _get_installed_apps(self) -> List[AppSnapshot]:
        """
        Get list of currently installed apps

        Returns:
            List of installed apps
        """
        apps = []
        system = platform.system()

        try:
            if system == "Darwin":  # macOS
                apps.extend(await self._get_brew_apps())
            elif system == "Linux":
                apps.extend(await self._get_apt_apps())
                apps.extend(await self._get_snap_apps())
            elif system == "Windows":
                apps.extend(await self._get_winget_apps())

        except Exception as e:
            logger.error(f"Failed to get installed apps: {e}")

        return apps

    async def _get_brew_apps(self) -> List[AppSnapshot]:
        """Get Homebrew installed apps"""
        apps = []

        try:
            # Get formulas
            result = subprocess.run(
                ['brew', 'list', '--formula', '--versions'],
                capture_output=True,
                text=True,
                timeout=10
            )

            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split()
                    if len(parts) >= 2:
                        apps.append(AppSnapshot(
                            name=parts[0],
                            package_id=parts[0],
                            version=parts[1],
                            install_method='brew',
                            install_time=time.time()
                        ))

            # Get casks
            result = subprocess.run(
                ['brew', 'list', '--cask', '--versions'],
                capture_output=True,
                text=True,
                timeout=10
            )

            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split()
                    if len(parts) >= 2:
                        apps.append(AppSnapshot(
                            name=parts[0],
                            package_id=parts[0],
                            version=parts[1],
                            install_method='cask',
                            install_time=time.time()
                        ))

        except Exception as e:
            logger.error(f"Failed to get brew apps: {e}")

        return apps

    async def _get_apt_apps(self) -> List[AppSnapshot]:
        """Get apt installed apps (Ubuntu/Debian)"""
        apps = []

        try:
            result = subprocess.run(
                ['dpkg', '-l'],
                capture_output=True,
                text=True,
                timeout=10
            )

            for line in result.stdout.split('\n'):
                if line.startswith('ii'):
                    parts = line.split()
                    if len(parts) >= 3:
                        apps.append(AppSnapshot(
                            name=parts[1],
                            package_id=parts[1],
                            version=parts[2],
                            install_method='apt',
                            install_time=time.time()
                        ))

        except Exception as e:
            logger.error(f"Failed to get apt apps: {e}")

        return apps

    async def _get_snap_apps(self) -> List[AppSnapshot]:
        """Get snap installed apps"""
        apps = []

        try:
            result = subprocess.run(
                ['snap', 'list'],
                capture_output=True,
                text=True,
                timeout=10
            )

            for line in result.stdout.split('\n')[1:]:  # Skip header
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        apps.append(AppSnapshot(
                            name=parts[0],
                            package_id=parts[0],
                            version=parts[1],
                            install_method='snap',
                            install_time=time.time()
                        ))

        except Exception as e:
            logger.error(f"Failed to get snap apps: {e}")

        return apps

    async def _get_winget_apps(self) -> List[AppSnapshot]:
        """Get winget installed apps (Windows)"""
        apps = []

        try:
            result = subprocess.run(
                ['winget', 'list'],
                capture_output=True,
                text=True,
                timeout=30
            )

            for line in result.stdout.split('\n')[2:]:  # Skip headers
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        apps.append(AppSnapshot(
                            name=parts[0],
                            package_id=parts[0],
                            version=parts[1] if len(parts) > 1 else 'unknown',
                            install_method='winget',
                            install_time=time.time()
                        ))

        except Exception as e:
            logger.error(f"Failed to get winget apps: {e}")

        return apps

    async def rollback(self, snapshot_id: str) -> bool:
        """
        Rollback to a specific snapshot

        Args:
            snapshot_id: ID of snapshot to rollback to

        Returns:
            True if rollback successful
        """
        if snapshot_id not in self.snapshots:
            logger.error(f"Snapshot not found: {snapshot_id}")
            return False

        logger.info(f"🔄 Rolling back to snapshot: {snapshot_id}")

        await self.event_bus.emit(Event(
            type=EventType.ROLLBACK_INITIATED,
            data={'snapshot_id': snapshot_id},
            source='rollback_manager'
        ))

        try:
            snapshot = self.snapshots[snapshot_id]
            current_apps = await self._get_installed_apps()

            # Find apps to remove (installed after snapshot)
            snapshot_app_ids = {app.package_id for app in snapshot.installed_apps}
            current_app_ids = {app.package_id for app in current_apps}

            apps_to_remove = current_app_ids - snapshot_app_ids

            logger.info(f"Will remove {len(apps_to_remove)} app(s)")

            # Uninstall apps
            for app in current_apps:
                if app.package_id in apps_to_remove:
                    await self._uninstall_app(app)

            await self.event_bus.emit(Event(
                type=EventType.ROLLBACK_COMPLETED,
                data={
                    'snapshot_id': snapshot_id,
                    'removed_apps': len(apps_to_remove)
                },
                source='rollback_manager'
            ))

            logger.info(f"✅ Rollback completed successfully")
            return True

        except Exception as e:
            logger.error(f"Rollback failed: {e}")

            await self.event_bus.emit(Event(
                type=EventType.ROLLBACK_FAILED,
                data={'snapshot_id': snapshot_id, 'error': str(e)},
                source='rollback_manager'
            ))

            return False

    async def _uninstall_app(self, app: AppSnapshot):
        """Uninstall a single app"""
        logger.info(f"Uninstalling {app.name} ({app.install_method})")

        try:
            if app.install_method == 'brew':
                subprocess.run(['brew', 'uninstall', app.package_id], check=True)
            elif app.install_method == 'cask':
                subprocess.run(['brew', 'uninstall', '--cask', app.package_id], check=True)
            elif app.install_method == 'apt':
                subprocess.run(['sudo', 'apt-get', 'remove', '-y', app.package_id], check=True)
            elif app.install_method == 'snap':
                subprocess.run(['sudo', 'snap', 'remove', app.package_id], check=True)
            elif app.install_method == 'winget':
                subprocess.run(['winget', 'uninstall', app.package_id], check=True)

            logger.info(f"✓ Uninstalled {app.name}")

        except Exception as e:
            logger.error(f"Failed to uninstall {app.name}: {e}")

    def list_snapshots(self) -> List[Dict[str, Any]]:
        """List all snapshots"""
        return [
            {
                'id': snapshot.id,
                'timestamp': snapshot.timestamp,
                'description': snapshot.description,
                'app_count': len(snapshot.installed_apps),
                'date': datetime.fromtimestamp(snapshot.timestamp).isoformat()
            }
            for snapshot in self.snapshots.values()
        ]

    def get_snapshot(self, snapshot_id: str) -> Optional[SystemSnapshot]:
        """Get snapshot by ID"""
        return self.snapshots.get(snapshot_id)

    def delete_snapshot(self, snapshot_id: str) -> bool:
        """Delete a snapshot"""
        if snapshot_id in self.snapshots:
            del self.snapshots[snapshot_id]
            self._save_snapshots()
            logger.info(f"🗑️  Deleted snapshot: {snapshot_id}")
            return True
        return False


# Import os for environment variables
import os


# Example usage
if __name__ == "__main__":
    async def example():
        rollback_mgr = RollbackManager()

        # Create snapshot
        snapshot_id = await rollback_mgr.create_snapshot("Before installing new apps")

        print(f"\nCreated snapshot: {snapshot_id}")

        # List snapshots
        print("\nAvailable snapshots:")
        for snap in rollback_mgr.list_snapshots():
            print(f"  - {snap['id']}: {snap['description']} ({snap['app_count']} apps)")

    asyncio.run(example())
