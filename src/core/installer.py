"""
Package Installer with Event System Integration
Handles actual package installation using platform package managers
"""

import asyncio
import subprocess
import platform
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from .event_system import EventBus, Event, EventType, get_event_bus


class InstallMethod(Enum):
    """Installation method types"""
    BREW = "brew"
    BREW_CASK = "cask"
    APT = "apt"
    DNF = "dnf"
    PACMAN = "pacman"
    SNAP = "snap"
    WINGET = "winget"
    CHOCOLATEY = "choco"
    MANUAL = "manual"


@dataclass
class Package:
    """Represents an installable package"""
    name: str
    package: str
    platforms: List[str]
    install_type: str
    category: str = "other"
    post_install: Optional[str] = None
    pre_install: Optional[str] = None
    notes: Optional[str] = None
    priority: str = "medium"
    size: Optional[str] = None
    version: Optional[str] = None


class PackageInstaller:
    """
    Handles package installation with event system integration
    """

    def __init__(self, event_bus: Optional[EventBus] = None):
        self.event_bus = event_bus or get_event_bus()
        self.platform_info = {'os': platform.system()}
        self.packages_db = self._load_packages()

    def _load_packages(self) -> Dict[str, Package]:
        """Load packages from apps.yaml"""
        apps_file = Path(__file__).parent.parent.parent / "apps.yaml"

        if not apps_file.exists():
            return {}

        with open(apps_file, 'r') as f:
            data = yaml.safe_load(f)

        packages = {}

        if not data or 'apps' not in data:
            return packages

        # Parse all categories
        for category, apps in data['apps'].items():
            for app in apps:
                pkg_name = app.get('name', '').lower().replace(' ', '-')
                packages[pkg_name] = Package(
                    name=app.get('name', pkg_name),
                    package=app.get('package', pkg_name),
                    platforms=app.get('platforms', []),
                    install_type=app.get('install_type', 'brew'),
                    category=category,
                    post_install=app.get('post_install'),
                    pre_install=app.get('pre_install'),
                    notes=app.get('notes'),
                    priority=app.get('priority', 'medium'),
                    size=app.get('size'),
                    version=app.get('version')
                )

        return packages

    def search_packages(self, query: str) -> List[Package]:
        """Search for packages matching query"""
        query = query.lower()
        results = []

        for pkg_name, pkg in self.packages_db.items():
            if (query in pkg_name.lower() or
                query in pkg.name.lower() or
                query in pkg.category.lower() or
                (pkg.notes and query in pkg.notes.lower())):
                results.append(pkg)

        return results

    def get_package(self, name: str) -> Optional[Package]:
        """Get package by name"""
        name = name.lower().replace(' ', '-')
        return self.packages_db.get(name)

    def list_packages(self, category: Optional[str] = None) -> List[Package]:
        """List all packages, optionally filtered by category"""
        packages = list(self.packages_db.values())

        if category:
            packages = [p for p in packages if p.category == category]

        return sorted(packages, key=lambda p: p.name)

    def get_categories(self) -> List[str]:
        """Get list of all categories"""
        categories = set(pkg.category for pkg in self.packages_db.values())
        return sorted(categories)

    async def is_installed(self, package_name: str) -> bool:
        """Check if a package is already installed"""
        pkg = self.get_package(package_name)
        if not pkg:
            return False

        # Determine package manager command
        if self.platform_info['os'] == 'Darwin':  # macOS
            if pkg.install_type == 'cask':
                cmd = ['brew', 'list', '--cask', pkg.package]
            else:
                cmd = ['brew', 'list', pkg.package]

        elif self.platform_info['os'] == 'Linux':
            # Try common package managers
            if pkg.install_type == 'apt':
                cmd = ['dpkg', '-l', pkg.package]
            elif pkg.install_type == 'snap':
                cmd = ['snap', 'list', pkg.package]
            else:
                cmd = ['which', pkg.package]

        else:
            # Windows
            return False  # TODO: Implement Windows detection

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    async def install(self, package_name: str, dry_run: bool = False) -> Dict[str, Any]:
        """
        Install a package with event system integration

        Args:
            package_name: Name of package to install
            dry_run: If True, only simulate installation

        Returns:
            Dictionary with installation result
        """
        pkg = self.get_package(package_name)

        if not pkg:
            await self.event_bus.emit(Event(
                type=EventType.INSTALL_FAILED,
                data={
                    'app': package_name,
                    'error': f'Package not found: {package_name}'
                },
                source='installer'
            ))
            return {'success': False, 'error': 'Package not found'}

        # Check if already installed
        if await self.is_installed(package_name):
            print(f"  ℹ️  {pkg.name} is already installed")
            return {'success': True, 'already_installed': True}

        # Emit install started event
        await self.event_bus.emit(Event(
            type=EventType.INSTALL_STARTED,
            data={
                'app': pkg.name,
                'package': pkg.package,
                'category': pkg.category
            },
            source='installer'
        ))

        try:
            # Run pre-install script if exists
            if pkg.pre_install and not dry_run:
                await self._run_script(pkg.pre_install, f"Pre-install for {pkg.name}")

            # Build install command
            install_cmd = self._build_install_command(pkg)

            if dry_run:
                print(f"  🔍 Would run: {' '.join(install_cmd)}")
                return {'success': True, 'dry_run': True, 'command': install_cmd}

            # Execute installation
            print(f"  ⬇️  Installing {pkg.name}...")
            result = await self._run_command(install_cmd, pkg.name)

            if result['success']:
                # Run post-install script if exists
                if pkg.post_install:
                    print(f"  ⚙️  Running post-install script...")
                    await self._run_script(pkg.post_install, f"Post-install for {pkg.name}")

                # Emit success event
                await self.event_bus.emit(Event(
                    type=EventType.INSTALL_COMPLETED,
                    data={
                        'app': pkg.name,
                        'package': pkg.package,
                        'success': True
                    },
                    source='installer'
                ))

                print(f"  ✅ {pkg.name} installed successfully")
                return {'success': True, 'package': pkg.name}

            else:
                # Emit failure event
                await self.event_bus.emit(Event(
                    type=EventType.INSTALL_FAILED,
                    data={
                        'app': pkg.name,
                        'error': result.get('error', 'Unknown error')
                    },
                    source='installer'
                ))

                return result

        except Exception as e:
            error_msg = str(e)

            await self.event_bus.emit(Event(
                type=EventType.INSTALL_FAILED,
                data={
                    'app': pkg.name,
                    'error': error_msg
                },
                source='installer'
            ))

            return {'success': False, 'error': error_msg}

    def _build_install_command(self, pkg: Package) -> List[str]:
        """Build installation command based on platform and package type"""
        if self.platform_info['os'] == 'Darwin':  # macOS
            if pkg.install_type == 'cask':
                return ['brew', 'install', '--cask', pkg.package]
            else:
                return ['brew', 'install', pkg.package]

        elif self.platform_info['os'] == 'Linux':
            if pkg.install_type == 'apt':
                return ['sudo', 'apt-get', 'install', '-y', pkg.package]
            elif pkg.install_type == 'snap':
                return ['sudo', 'snap', 'install', pkg.package]
            elif pkg.install_type == 'dnf':
                return ['sudo', 'dnf', 'install', '-y', pkg.package]
            else:
                return ['brew', 'install', pkg.package]

        else:  # Windows
            if pkg.install_type == 'winget':
                return ['winget', 'install', pkg.package, '-e']
            elif pkg.install_type == 'choco':
                return ['choco', 'install', pkg.package, '-y']

        return []

    async def _run_command(self, cmd: List[str], app_name: str) -> Dict[str, Any]:
        """Run installation command asynchronously"""
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                return {'success': True}
            else:
                error = stderr.decode() if stderr else 'Unknown error'
                return {'success': False, 'error': error}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def _run_script(self, script: str, description: str):
        """Run a shell script"""
        try:
            process = await asyncio.create_subprocess_shell(
                script,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
        except Exception as e:
            print(f"  ⚠️  Warning: {description} failed: {e}")

    async def uninstall(self, package_name: str) -> Dict[str, Any]:
        """Uninstall a package"""
        pkg = self.get_package(package_name)

        if not pkg:
            return {'success': False, 'error': 'Package not found'}

        # Check if installed
        if not await self.is_installed(package_name):
            print(f"  ℹ️  {pkg.name} is not installed")
            return {'success': True, 'not_installed': True}

        # Emit uninstall started event
        await self.event_bus.emit(Event(
            type=EventType.UNINSTALL_STARTED,
            data={'app': pkg.name},
            source='installer'
        ))

        try:
            # Build uninstall command
            if self.platform_info['os'] == 'Darwin':
                if pkg.install_type == 'cask':
                    cmd = ['brew', 'uninstall', '--cask', pkg.package]
                else:
                    cmd = ['brew', 'uninstall', pkg.package]
            else:
                # TODO: Add Linux/Windows uninstall commands
                return {'success': False, 'error': 'Uninstall not yet supported on this platform'}

            print(f"  🗑️  Uninstalling {pkg.name}...")
            result = await self._run_command(cmd, pkg.name)

            if result['success']:
                await self.event_bus.emit(Event(
                    type=EventType.UNINSTALL_COMPLETED,
                    data={'app': pkg.name},
                    source='installer'
                ))
                print(f"  ✅ {pkg.name} uninstalled successfully")

            return result

        except Exception as e:
            await self.event_bus.emit(Event(
                type=EventType.UNINSTALL_FAILED,
                data={'app': pkg.name, 'error': str(e)},
                source='installer'
            ))
            return {'success': False, 'error': str(e)}

    async def update(self, package_name: str) -> Dict[str, Any]:
        """Update a package to latest version"""
        pkg = self.get_package(package_name)

        if not pkg:
            return {'success': False, 'error': 'Package not found'}

        # Emit update started event
        await self.event_bus.emit(Event(
            type=EventType.UPDATE_STARTED,
            data={'app': pkg.name},
            source='installer'
        ))

        try:
            # Build update command
            if self.platform_info['os'] == 'Darwin':
                cmd = ['brew', 'upgrade', pkg.package]
            else:
                # TODO: Add Linux/Windows update commands
                return {'success': False, 'error': 'Update not yet supported on this platform'}

            print(f"  ⬆️  Updating {pkg.name}...")
            result = await self._run_command(cmd, pkg.name)

            if result['success']:
                await self.event_bus.emit(Event(
                    type=EventType.UPDATE_COMPLETED,
                    data={'app': pkg.name},
                    source='installer'
                ))
                print(f"  ✅ {pkg.name} updated successfully")

            return result

        except Exception as e:
            await self.event_bus.emit(Event(
                type=EventType.UPDATE_FAILED,
                data={'app': pkg.name, 'error': str(e)},
                source='installer'
            ))
            return {'success': False, 'error': str(e)}


# Singleton instance
_installer = None


def get_installer() -> PackageInstaller:
    """Get singleton installer instance"""
    global _installer
    if _installer is None:
        _installer = PackageInstaller()
    return _installer
