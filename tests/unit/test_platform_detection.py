#!/usr/bin/env python3
"""
Unit tests for platform detection module
Tests WSL2 detection, architecture detection, and distribution detection
"""

import pytest
import platform
import sys
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.platform_detection import (
    PlatformDetector,
    PlatformType,
    Architecture,
    get_platform,
    is_wsl,
    is_wsl2,
    is_macos,
    is_linux,
    is_apple_silicon
)


class TestArchitectureDetection:
    """Test architecture detection"""

    @patch('platform.machine')
    def test_detect_x86_64(self, mock_machine):
        """Test x86_64 detection"""
        mock_machine.return_value = 'x86_64'
        arch = PlatformDetector._detect_architecture()
        assert arch == Architecture.X86_64

    @patch('platform.machine')
    def test_detect_amd64(self, mock_machine):
        """Test amd64 is mapped to x86_64"""
        mock_machine.return_value = 'amd64'
        arch = PlatformDetector._detect_architecture()
        assert arch == Architecture.X86_64

    @patch('platform.machine')
    def test_detect_arm64(self, mock_machine):
        """Test ARM64 detection (Apple Silicon)"""
        mock_machine.return_value = 'arm64'
        arch = PlatformDetector._detect_architecture()
        assert arch == Architecture.ARM64

    @patch('platform.machine')
    def test_detect_unknown(self, mock_machine):
        """Test unknown architecture"""
        mock_machine.return_value = 'unknown_arch'
        arch = PlatformDetector._detect_architecture()
        assert arch == Architecture.UNKNOWN


class TestWSLDetection:
    """Test WSL detection with multiple fallback methods"""

    def test_wsl_detect_proc_version(self):
        """Test WSL detection via /proc/version"""
        with patch('pathlib.Path.exists') as mock_exists:
            with patch('builtins.open', mock_open(read_data='Linux version 5.10.16.3-microsoft-standard-WSL2')):
                mock_exists.return_value = True
                is_wsl_detected, wsl_version = PlatformDetector._detect_wsl()
                assert is_wsl_detected is True
                assert wsl_version == 2

    def test_wsl_detect_env_var(self):
        """Test WSL detection via environment variable"""
        with patch.dict('os.environ', {'WSL_DISTRO_NAME': 'Ubuntu'}):
            with patch('pathlib.Path.exists', return_value=False):
                with patch('platform.release', return_value='5.10.16.3-microsoft-standard-WSL2'):
                    is_wsl_detected, wsl_version = PlatformDetector._detect_wsl()
                    # Should detect WSL based on env var
                    assert is_wsl_detected is True

    def test_wsl2_detect_run_directory(self):
        """Test WSL2 detection via /run/WSL directory"""
        def mock_exists(path):
            return str(path) == "/run/WSL"

        with patch.object(Path, 'exists', side_effect=mock_exists):
            is_wsl_detected, wsl_version = PlatformDetector._detect_wsl()
            assert is_wsl_detected is True
            assert wsl_version == 2

    def test_wsl2_detect_binfmt_misc(self):
        """Test WSL2 detection via binfmt_misc"""
        def mock_exists(path):
            return str(path) == "/proc/sys/fs/binfmt_misc/WSLInterop"

        with patch.object(Path, 'exists', side_effect=mock_exists):
            is_wsl_detected, wsl_version = PlatformDetector._detect_wsl()
            assert is_wsl_detected is True
            assert wsl_version == 2

    def test_non_wsl_linux(self):
        """Test regular Linux (not WSL)"""
        with patch('pathlib.Path.exists', return_value=False):
            with patch('platform.release', return_value='5.15.0-generic'):
                with patch.dict('os.environ', {}, clear=True):
                    is_wsl_detected, wsl_version = PlatformDetector._detect_wsl()
                    assert is_wsl_detected is False
                    assert wsl_version is None


class TestMacOSDetection:
    """Test macOS detection"""

    @patch('platform.system')
    @patch('platform.mac_ver')
    @patch('platform.machine')
    def test_detect_macos_intel(self, mock_machine, mock_mac_ver, mock_system):
        """Test macOS Intel detection"""
        mock_system.return_value = 'Darwin'
        mock_mac_ver.return_value = ('13.0', '', '')
        mock_machine.return_value = 'x86_64'

        info = PlatformDetector.detect()

        assert info.platform_type == PlatformType.MACOS
        assert info.architecture == Architecture.X86_64
        assert info.os_version == '13.0'
        assert info.additional_info.get('is_apple_silicon') is False

    @patch('platform.system')
    @patch('platform.mac_ver')
    @patch('platform.machine')
    def test_detect_macos_apple_silicon(self, mock_machine, mock_mac_ver, mock_system):
        """Test macOS Apple Silicon detection"""
        mock_system.return_value = 'Darwin'
        mock_mac_ver.return_value = ('14.0', '', '')
        mock_machine.return_value = 'arm64'

        info = PlatformDetector.detect()

        assert info.platform_type == PlatformType.MACOS
        assert info.architecture == Architecture.ARM64
        assert info.additional_info.get('is_apple_silicon') is True


class TestLinuxDistribution:
    """Test Linux distribution detection"""

    def test_detect_ubuntu_os_release(self):
        """Test Ubuntu detection via /etc/os-release"""
        os_release_content = '''NAME="Ubuntu"
VERSION="22.04.1 LTS (Jammy Jellyfish)"
ID=ubuntu
VERSION_ID="22.04"
'''
        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=os_release_content)):
                name, version = PlatformDetector._get_linux_distro_info()
                assert 'Ubuntu' in name
                assert version == '22.04'

    def test_detect_distro_fallback(self):
        """Test fallback distribution detection"""
        with patch('pathlib.Path.exists') as mock_exists:
            # /etc/os-release doesn't exist
            def exists_side_effect(path):
                if '/etc/debian_version' in str(path):
                    return True
                return False

            mock_exists.side_effect = exists_side_effect

            with patch('builtins.open', mock_open(read_data='12.0')):
                name, version = PlatformDetector._get_linux_distro_info()
                assert 'Debian' in name
                assert '12.0' in version


class TestPackageManagerDetection:
    """Test package manager detection"""

    @patch('subprocess.run')
    def test_detect_homebrew(self, mock_run):
        """Test Homebrew detection"""
        mock_run.return_value = MagicMock(returncode=0)

        managers = PlatformDetector._detect_package_managers()
        mock_run.assert_called()

    @patch('subprocess.run')
    def test_detect_multiple_managers(self, mock_run):
        """Test detection of multiple package managers"""
        # Simulate apt and snap being available
        def run_side_effect(cmd, *args, **kwargs):
            if 'apt' in cmd:
                return MagicMock(returncode=0)
            elif 'snap' in cmd:
                return MagicMock(returncode=0)
            else:
                return MagicMock(returncode=1)

        mock_run.side_effect = run_side_effect

        managers = PlatformDetector._detect_package_managers()
        # Should detect some managers (exact list depends on mocking)
        assert isinstance(managers, list)


class TestConvenienceFunctions:
    """Test convenience functions"""

    @patch('platform.system')
    def test_is_macos(self, mock_system):
        """Test is_macos function"""
        mock_system.return_value = 'Darwin'
        with patch('platform.mac_ver', return_value=('13.0', '', '')):
            assert is_macos() is True

    @patch('platform.system')
    def test_is_linux(self, mock_system):
        """Test is_linux function (not WSL)"""
        mock_system.return_value = 'Linux'
        with patch.object(PlatformDetector, '_detect_wsl', return_value=(False, None)):
            assert is_linux() is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
