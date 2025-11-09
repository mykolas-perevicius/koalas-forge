#!/usr/bin/env python3
"""
Platform Detection Module
Robust detection of operating systems, including WSL2 on Windows 11
"""

import os
import platform
import re
import subprocess
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any


class PlatformType(Enum):
    """Supported platform types"""
    MACOS = "macos"
    LINUX = "linux"
    WINDOWS = "windows"
    WSL1 = "wsl1"
    WSL2 = "wsl2"
    UNKNOWN = "unknown"


class Architecture(Enum):
    """CPU architectures"""
    X86_64 = "x86_64"
    ARM64 = "arm64"
    AARCH64 = "aarch64"
    I386 = "i386"
    UNKNOWN = "unknown"


@dataclass
class PlatformInfo:
    """Complete platform information"""
    platform_type: PlatformType
    architecture: Architecture
    os_version: str
    distribution: Optional[str] = None  # For Linux
    distribution_version: Optional[str] = None
    kernel_version: Optional[str] = None
    is_virtual: bool = False
    wsl_version: Optional[int] = None  # 1 or 2
    additional_info: Dict[str, Any] = None

    def __post_init__(self):
        if self.additional_info is None:
            self.additional_info = {}


class PlatformDetector:
    """
    Detect platform with multiple fallback mechanisms

    Critical fixes for Week 1-2 Stabilization Sprint:
    - WSL2 detection using multiple indicators
    - Apple Silicon detection
    - Linux distribution detection improvements
    """

    @staticmethod
    def detect() -> PlatformInfo:
        """Main detection entry point"""
        # Detect architecture first
        arch = PlatformDetector._detect_architecture()

        # Detect platform type
        system = platform.system().lower()

        if system == "darwin":
            return PlatformDetector._detect_macos(arch)
        elif system == "linux":
            return PlatformDetector._detect_linux(arch)
        elif system == "windows":
            return PlatformDetector._detect_windows(arch)
        else:
            return PlatformInfo(
                platform_type=PlatformType.UNKNOWN,
                architecture=arch,
                os_version=platform.version()
            )

    @staticmethod
    def _detect_architecture() -> Architecture:
        """Detect CPU architecture"""
        machine = platform.machine().lower()

        # Map various architecture names to our enum
        arch_map = {
            "x86_64": Architecture.X86_64,
            "amd64": Architecture.X86_64,
            "arm64": Architecture.ARM64,
            "aarch64": Architecture.AARCH64,
            "i386": Architecture.I386,
            "i686": Architecture.I386,
        }

        return arch_map.get(machine, Architecture.UNKNOWN)

    @staticmethod
    def _detect_macos(arch: Architecture) -> PlatformInfo:
        """Detect macOS version and features"""
        try:
            # Get macOS version
            version = platform.mac_ver()[0]

            # Detect if running on Apple Silicon
            is_apple_silicon = arch in (Architecture.ARM64, Architecture.AARCH64)

            # Get detailed system info
            additional_info = {
                "is_apple_silicon": is_apple_silicon,
                "can_run_rosetta": is_apple_silicon
            }

            # Check if Rosetta 2 is installed (for Apple Silicon)
            if is_apple_silicon:
                try:
                    result = subprocess.run(
                        ["/usr/bin/pgrep", "oahd"],
                        capture_output=True,
                        timeout=2
                    )
                    additional_info["rosetta_installed"] = result.returncode == 0
                except:
                    additional_info["rosetta_installed"] = False

            return PlatformInfo(
                platform_type=PlatformType.MACOS,
                architecture=arch,
                os_version=version,
                kernel_version=platform.release(),
                additional_info=additional_info
            )
        except Exception as e:
            return PlatformInfo(
                platform_type=PlatformType.MACOS,
                architecture=arch,
                os_version="unknown",
                additional_info={"error": str(e)}
            )

    @staticmethod
    def _detect_linux(arch: Architecture) -> PlatformInfo:
        """
        Detect Linux distribution and check for WSL

        CRITICAL FIX: Multiple WSL2 detection methods
        """
        # First, check if we're in WSL
        is_wsl, wsl_version = PlatformDetector._detect_wsl()

        if is_wsl:
            return PlatformDetector._detect_wsl_details(arch, wsl_version)

        # Regular Linux detection
        return PlatformDetector._detect_linux_distro(arch)

    @staticmethod
    def _detect_wsl() -> tuple[bool, Optional[int]]:
        """
        Detect WSL with multiple fallback methods

        CRITICAL FIX for WSL2 detection on Windows 11
        This checks multiple indicators instead of relying on a single registry key
        """
        wsl_indicators = []

        # Method 1: Check /proc/version for WSL/Microsoft
        try:
            if Path("/proc/version").exists():
                with open("/proc/version", "r") as f:
                    proc_version = f.read().lower()
                    if "microsoft" in proc_version or "wsl" in proc_version:
                        wsl_indicators.append("proc_version")
                        # WSL2 uses a Microsoft kernel
                        if "microsoft" in proc_version and "wsl2" in proc_version:
                            return True, 2
        except:
            pass

        # Method 2: Check kernel version
        try:
            kernel = platform.release().lower()
            if "microsoft" in kernel or "wsl" in kernel:
                wsl_indicators.append("kernel")
        except:
            pass

        # Method 3: Check for WSL-specific environment variable
        if os.getenv("WSL_DISTRO_NAME"):
            wsl_indicators.append("env_var")

        # Method 4: Check /proc/sys/kernel/osrelease
        try:
            osrelease_path = Path("/proc/sys/kernel/osrelease")
            if osrelease_path.exists():
                with open(osrelease_path, "r") as f:
                    osrelease = f.read().lower()
                    if "microsoft" in osrelease or "wsl" in osrelease:
                        wsl_indicators.append("osrelease")
        except:
            pass

        # Method 5: Check for /run/WSL directory (WSL2 specific)
        if Path("/run/WSL").exists():
            wsl_indicators.append("run_wsl")
            return True, 2

        # Method 6: Check for wsl.exe or wslhost.exe presence
        try:
            # In WSL, we can access Windows executables
            result = subprocess.run(
                ["which", "wsl.exe"],
                capture_output=True,
                timeout=2
            )
            if result.returncode == 0:
                wsl_indicators.append("wsl_exe")
        except:
            pass

        # Method 7: Check /proc/sys/fs/binfmt_misc/WSLInterop (WSL2)
        if Path("/proc/sys/fs/binfmt_misc/WSLInterop").exists():
            wsl_indicators.append("binfmt_misc")
            return True, 2

        # Determine if we're in WSL based on indicators
        if len(wsl_indicators) >= 2:
            # If we have 2+ indicators, we're definitely in WSL
            # Try to determine version

            # Check for WSL2-specific indicators
            wsl2_indicators = {"run_wsl", "binfmt_misc"}
            if any(indicator in wsl2_indicators for indicator in wsl_indicators):
                return True, 2

            # Check kernel version for WSL2 (uses native Linux kernel 4.19+)
            try:
                kernel_version = platform.release()
                version_match = re.search(r"(\d+)\.(\d+)", kernel_version)
                if version_match:
                    major, minor = int(version_match.group(1)), int(version_match.group(2))
                    if major >= 4 and minor >= 19:
                        return True, 2  # Likely WSL2
                    else:
                        return True, 1  # Likely WSL1
            except:
                pass

            # Default to WSL1 if we can't determine
            return True, 1

        return False, None

    @staticmethod
    def _detect_wsl_details(arch: Architecture, wsl_version: Optional[int]) -> PlatformInfo:
        """Get detailed WSL information"""
        # Get Linux distribution info
        distro_name, distro_version = PlatformDetector._get_linux_distro_info()

        platform_type = PlatformType.WSL2 if wsl_version == 2 else PlatformType.WSL1

        additional_info = {
            "wsl_version": wsl_version,
            "wsl_distro_name": os.getenv("WSL_DISTRO_NAME", "unknown"),
            "host_os": "windows"
        }

        return PlatformInfo(
            platform_type=platform_type,
            architecture=arch,
            os_version=platform.version(),
            distribution=distro_name,
            distribution_version=distro_version,
            kernel_version=platform.release(),
            is_virtual=True,
            wsl_version=wsl_version,
            additional_info=additional_info
        )

    @staticmethod
    def _detect_linux_distro(arch: Architecture) -> PlatformInfo:
        """Detect Linux distribution details"""
        distro_name, distro_version = PlatformDetector._get_linux_distro_info()

        # Check if running in a container/VM
        is_virtual = PlatformDetector._check_virtualization()

        additional_info = {
            "is_container": PlatformDetector._is_container(),
            "package_managers": PlatformDetector._detect_package_managers()
        }

        return PlatformInfo(
            platform_type=PlatformType.LINUX,
            architecture=arch,
            os_version=platform.version(),
            distribution=distro_name,
            distribution_version=distro_version,
            kernel_version=platform.release(),
            is_virtual=is_virtual,
            additional_info=additional_info
        )

    @staticmethod
    def _get_linux_distro_info() -> tuple[Optional[str], Optional[str]]:
        """
        Get Linux distribution name and version

        Uses multiple methods for better compatibility
        """
        # Method 1: /etc/os-release (most common)
        try:
            if Path("/etc/os-release").exists():
                with open("/etc/os-release", "r") as f:
                    os_release = {}
                    for line in f:
                        if "=" in line:
                            key, value = line.strip().split("=", 1)
                            os_release[key] = value.strip('"')

                    name = os_release.get("NAME") or os_release.get("ID")
                    version = os_release.get("VERSION_ID") or os_release.get("VERSION")

                    if name:
                        return name, version
        except:
            pass

        # Method 2: lsb_release command
        try:
            result = subprocess.run(
                ["lsb_release", "-a"],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                name = None
                version = None
                for line in lines:
                    if "Distributor ID:" in line:
                        name = line.split(":", 1)[1].strip()
                    elif "Release:" in line:
                        version = line.split(":", 1)[1].strip()
                if name:
                    return name, version
        except:
            pass

        # Method 3: Check various release files
        release_files = [
            "/etc/redhat-release",
            "/etc/debian_version",
            "/etc/arch-release",
            "/etc/alpine-release"
        ]

        for release_file in release_files:
            try:
                if Path(release_file).exists():
                    with open(release_file, "r") as f:
                        content = f.read().strip()
                        # Extract distribution name from file path
                        distro = Path(release_file).stem.replace("-release", "").replace("_version", "")
                        return distro.capitalize(), content
            except:
                continue

        return None, None

    @staticmethod
    def _detect_package_managers() -> list[str]:
        """Detect available package managers"""
        managers = []

        # Common package managers to check
        pm_commands = {
            "apt": ["apt", "--version"],
            "dnf": ["dnf", "--version"],
            "yum": ["yum", "--version"],
            "pacman": ["pacman", "--version"],
            "zypper": ["zypper", "--version"],
            "apk": ["apk", "--version"],
            "brew": ["brew", "--version"],
            "snap": ["snap", "--version"],
            "flatpak": ["flatpak", "--version"]
        }

        for pm_name, pm_cmd in pm_commands.items():
            try:
                result = subprocess.run(
                    pm_cmd,
                    capture_output=True,
                    timeout=2
                )
                if result.returncode == 0:
                    managers.append(pm_name)
            except:
                pass

        return managers

    @staticmethod
    def _check_virtualization() -> bool:
        """Check if running in a virtual environment"""
        # Check systemd-detect-virt
        try:
            result = subprocess.run(
                ["systemd-detect-virt"],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                virt_type = result.stdout.strip()
                return virt_type != "none"
        except:
            pass

        # Check /proc/cpuinfo for hypervisor flag
        try:
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if "hypervisor" in line.lower():
                        return True
        except:
            pass

        return False

    @staticmethod
    def _is_container() -> bool:
        """Check if running in a container"""
        # Check for /.dockerenv
        if Path("/.dockerenv").exists():
            return True

        # Check /proc/1/cgroup
        try:
            with open("/proc/1/cgroup", "r") as f:
                content = f.read()
                if "docker" in content or "lxc" in content or "kubepods" in content:
                    return True
        except:
            pass

        return False

    @staticmethod
    def _detect_windows(arch: Architecture) -> PlatformInfo:
        """Detect Windows version"""
        version = platform.version()
        release = platform.release()

        additional_info = {
            "release": release,
            "edition": platform.win32_edition() if hasattr(platform, "win32_edition") else "unknown"
        }

        return PlatformInfo(
            platform_type=PlatformType.WINDOWS,
            architecture=arch,
            os_version=version,
            additional_info=additional_info
        )


# Convenience functions
def get_platform() -> PlatformInfo:
    """Get current platform information"""
    return PlatformDetector.detect()


def is_wsl() -> bool:
    """Check if running in WSL"""
    platform_info = get_platform()
    return platform_info.platform_type in (PlatformType.WSL1, PlatformType.WSL2)


def is_wsl2() -> bool:
    """Check if running in WSL2"""
    platform_info = get_platform()
    return platform_info.platform_type == PlatformType.WSL2


def is_macos() -> bool:
    """Check if running on macOS"""
    return get_platform().platform_type == PlatformType.MACOS


def is_linux() -> bool:
    """Check if running on Linux (not WSL)"""
    return get_platform().platform_type == PlatformType.LINUX


def is_apple_silicon() -> bool:
    """Check if running on Apple Silicon"""
    platform_info = get_platform()
    if platform_info.platform_type == PlatformType.MACOS:
        return platform_info.additional_info.get("is_apple_silicon", False)
    return False


if __name__ == "__main__":
    # Test detection
    info = get_platform()
    print(f"Platform: {info.platform_type.value}")
    print(f"Architecture: {info.architecture.value}")
    print(f"OS Version: {info.os_version}")

    if info.distribution:
        print(f"Distribution: {info.distribution} {info.distribution_version or ''}")

    if info.kernel_version:
        print(f"Kernel: {info.kernel_version}")

    if info.wsl_version:
        print(f"WSL Version: {info.wsl_version}")

    if info.additional_info:
        print(f"Additional Info: {info.additional_info}")
