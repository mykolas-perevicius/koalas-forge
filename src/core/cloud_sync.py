#!/usr/bin/env python3
"""
Cloud Sync Scaffolding for Koala's Forge
Simple file-based sync using existing cloud providers (Dropbox, iCloud, OneDrive)
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from cryptography.fernet import Fernet
import base64
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class SyncProfile:
    """Profile data for syncing"""
    name: str
    description: str
    apps: List[str]
    presets: List[str]
    created: str
    updated: str
    device_id: str
    version: int = 1


class SyncBackend(ABC):
    """Base class for sync backends"""

    @abstractmethod
    async def push(self, profile: SyncProfile, encrypted_data: bytes) -> bool:
        """Push profile to backend"""
        pass

    @abstractmethod
    async def pull(self, profile_name: str) -> Optional[bytes]:
        """Pull profile from backend"""
        pass

    @abstractmethod
    async def list_profiles(self) -> List[str]:
        """List available profiles"""
        pass

    @abstractmethod
    async def delete(self, profile_name: str) -> bool:
        """Delete profile from backend"""
        pass


class FileSyncBackend(SyncBackend):
    """
    Simple file-based sync using local directories
    Works with Dropbox, iCloud Drive, OneDrive, etc.
    """

    def __init__(self, sync_dir: Path):
        self.sync_dir = sync_dir
        self.sync_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"📁 File sync backend: {sync_dir}")

    async def push(self, profile: SyncProfile, encrypted_data: bytes) -> bool:
        """Push encrypted profile to sync directory"""
        try:
            filename = f"{profile.name}.kfprofile"
            file_path = self.sync_dir / filename

            # Write encrypted data
            with open(file_path, 'wb') as f:
                f.write(encrypted_data)

            # Write metadata
            metadata = {
                'name': profile.name,
                'device_id': profile.device_id,
                'updated': profile.updated,
                'version': profile.version
            }

            metadata_path = self.sync_dir / f"{profile.name}.metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)

            logger.info(f"✓ Pushed profile: {profile.name}")
            return True

        except Exception as e:
            logger.error(f"Failed to push profile: {e}")
            return False

    async def pull(self, profile_name: str) -> Optional[bytes]:
        """Pull encrypted profile from sync directory"""
        try:
            filename = f"{profile_name}.kfprofile"
            file_path = self.sync_dir / filename

            if not file_path.exists():
                logger.warning(f"Profile not found: {profile_name}")
                return None

            with open(file_path, 'rb') as f:
                encrypted_data = f.read()

            logger.info(f"✓ Pulled profile: {profile_name}")
            return encrypted_data

        except Exception as e:
            logger.error(f"Failed to pull profile: {e}")
            return None

    async def list_profiles(self) -> List[str]:
        """List available profiles in sync directory"""
        profiles = []

        for file_path in self.sync_dir.glob("*.kfprofile"):
            profile_name = file_path.stem
            profiles.append(profile_name)

        return profiles

    async def delete(self, profile_name: str) -> bool:
        """Delete profile from sync directory"""
        try:
            file_path = self.sync_dir / f"{profile_name}.kfprofile"
            metadata_path = self.sync_dir / f"{profile_name}.metadata.json"

            if file_path.exists():
                file_path.unlink()

            if metadata_path.exists():
                metadata_path.unlink()

            logger.info(f"🗑️ Deleted profile: {profile_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete profile: {e}")
            return False


class CloudSyncManager:
    """
    Manages profile synchronization with encryption
    """

    def __init__(self, passphrase: Optional[str] = None):
        self.device_id = self._get_device_id()
        self.encryption_key = self._derive_key(passphrase or "koalas-forge-default")
        self.cipher = Fernet(self.encryption_key)

        # Available backends
        self.backends: Dict[str, SyncBackend] = {}
        self._init_backends()

        logger.info(f"☁️ Cloud sync manager initialized (device: {self.device_id})")

    def _init_backends(self):
        """Initialize available sync backends"""
        # Check for common cloud storage locations
        home = Path.home()

        # Dropbox
        dropbox_dir = home / "Dropbox" / "KoalasForge"
        if dropbox_dir.parent.exists():
            self.backends['dropbox'] = FileSyncBackend(dropbox_dir)

        # iCloud Drive (macOS)
        icloud_dir = home / "Library" / "Mobile Documents" / "com~apple~CloudDocs" / "KoalasForge"
        if icloud_dir.parent.parent.exists():
            self.backends['icloud'] = FileSyncBackend(icloud_dir)

        # OneDrive
        onedrive_dir = home / "OneDrive" / "KoalasForge"
        if onedrive_dir.parent.exists():
            self.backends['onedrive'] = FileSyncBackend(onedrive_dir)

        # Google Drive
        gdrive_dir = home / "Google Drive" / "KoalasForge"
        if gdrive_dir.parent.exists():
            self.backends['gdrive'] = FileSyncBackend(gdrive_dir)

        # Fallback: Local sync folder
        if not self.backends:
            local_dir = home / ".koalas-forge" / "sync"
            self.backends['local'] = FileSyncBackend(local_dir)

        logger.info(f"Available backends: {list(self.backends.keys())}")

    def _derive_key(self, passphrase: str) -> bytes:
        """Derive encryption key from passphrase"""
        # Simple key derivation (should use PBKDF2 in production)
        key_material = hashlib.sha256(passphrase.encode()).digest()
        return base64.urlsafe_b64encode(key_material)

    def _get_device_id(self) -> str:
        """Get unique device identifier"""
        import platform
        import socket

        try:
            hostname = socket.gethostname()
            system = platform.system()
            machine = platform.machine()
            device_str = f"{hostname}-{system}-{machine}"
            return hashlib.md5(device_str.encode()).hexdigest()[:8]
        except:
            return "unknown"

    async def push_profile(self,
                          profile_data: Dict[str, Any],
                          backend: str = 'local') -> bool:
        """
        Push profile to cloud storage

        Args:
            profile_data: Profile data dictionary
            backend: Backend to use (dropbox, icloud, onedrive, local)

        Returns:
            True if successful
        """
        if backend not in self.backends:
            logger.error(f"Backend not available: {backend}")
            return False

        try:
            # Create SyncProfile
            profile = SyncProfile(
                name=profile_data['name'],
                description=profile_data.get('description', ''),
                apps=profile_data.get('apps', []),
                presets=profile_data.get('presets', []),
                created=profile_data.get('created', datetime.now().isoformat()),
                updated=datetime.now().isoformat(),
                device_id=self.device_id
            )

            # Encrypt profile data
            profile_json = json.dumps(asdict(profile)).encode()
            encrypted_data = self.cipher.encrypt(profile_json)

            # Push to backend
            success = await self.backends[backend].push(profile, encrypted_data)

            if success:
                logger.info(f"✓ Profile pushed to {backend}: {profile.name}")

            return success

        except Exception as e:
            logger.error(f"Failed to push profile: {e}")
            return False

    async def pull_profile(self,
                          profile_name: str,
                          backend: str = 'local') -> Optional[Dict[str, Any]]:
        """
        Pull profile from cloud storage

        Args:
            profile_name: Name of profile to pull
            backend: Backend to use

        Returns:
            Profile data dictionary or None
        """
        if backend not in self.backends:
            logger.error(f"Backend not available: {backend}")
            return None

        try:
            # Pull encrypted data
            encrypted_data = await self.backends[backend].pull(profile_name)

            if not encrypted_data:
                return None

            # Decrypt profile data
            decrypted_data = self.cipher.decrypt(encrypted_data)
            profile_dict = json.loads(decrypted_data)

            logger.info(f"✓ Profile pulled from {backend}: {profile_name}")
            return profile_dict

        except Exception as e:
            logger.error(f"Failed to pull profile: {e}")
            return None

    async def list_profiles(self, backend: str = 'local') -> List[str]:
        """List available profiles in backend"""
        if backend not in self.backends:
            return []

        return await self.backends[backend].list_profiles()

    async def delete_profile(self, profile_name: str, backend: str = 'local') -> bool:
        """Delete profile from backend"""
        if backend not in self.backends:
            return False

        return await self.backends[backend].delete(profile_name)

    def get_available_backends(self) -> List[str]:
        """Get list of available backends"""
        return list(self.backends.keys())

    def get_status(self) -> Dict[str, Any]:
        """Get sync status information"""
        backends = list(self.backends.keys())
        primary_backend = backends[0] if backends else 'none'

        status = {
            'enabled': len(backends) > 0,
            'backend': primary_backend,
            'backends': backends,
            'device_id': self.device_id,
        }

        # Add sync path if available
        if primary_backend != 'none' and primary_backend in self.backends:
            backend = self.backends[primary_backend]
            if hasattr(backend, 'sync_dir'):
                status['sync_path'] = str(backend.sync_dir)

        return status

    async def sync_profile(self,
                          profile_data: Dict[str, Any],
                          backends: Optional[List[str]] = None) -> Dict[str, bool]:
        """
        Sync profile to multiple backends

        Args:
            profile_data: Profile data
            backends: List of backends to sync to (None = all)

        Returns:
            Dictionary of backend: success status
        """
        if backends is None:
            backends = list(self.backends.keys())

        results = {}

        for backend in backends:
            success = await self.push_profile(profile_data, backend)
            results[backend] = success

        logger.info(f"Sync results: {results}")
        return results


# Example usage
if __name__ == "__main__":
    async def example():
        sync_mgr = CloudSyncManager(passphrase="my-secret-passphrase")

        # Show available backends
        print(f"Available backends: {sync_mgr.get_available_backends()}")

        # Create test profile
        test_profile = {
            'name': 'my-dev-setup',
            'description': 'My development environment',
            'apps': ['git', 'python', 'docker', 'vscode'],
            'presets': ['full-stack'],
            'created': datetime.now().isoformat()
        }

        # Push to all available backends
        results = await sync_mgr.sync_profile(test_profile)
        print(f"Sync results: {results}")

        # Pull from local
        pulled_profile = await sync_mgr.pull_profile('my-dev-setup', 'local')
        print(f"Pulled profile: {pulled_profile}")

    asyncio.run(example())
