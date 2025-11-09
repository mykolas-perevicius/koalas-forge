#!/usr/bin/env python3
"""
Error Handling Module
User-friendly error messages with recovery suggestions
"""

from enum import Enum
from typing import Optional, Dict, Any, List


class ErrorCategory(Enum):
    """Error categories for classification"""
    NETWORK = "network"
    PERMISSION = "permission"
    DEPENDENCY = "dependency"
    PLATFORM = "platform"
    DISK_SPACE = "disk_space"
    PACKAGE_MANAGER = "package_manager"
    CHECKSUM = "checksum"
    CONFIGURATION = "configuration"
    UNKNOWN = "unknown"


class ErrorSeverity(Enum):
    """Error severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class KoalasForgeError(Exception):
    """Base exception for Koala's Forge"""

    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        recovery_suggestions: Optional[List[str]] = None,
        technical_details: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.recovery_suggestions = recovery_suggestions or []
        self.technical_details = technical_details
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for JSON serialization"""
        return {
            "message": self.message,
            "category": self.category.value,
            "severity": self.severity.value,
            "recovery_suggestions": self.recovery_suggestions,
            "technical_details": self.technical_details,
            "metadata": self.metadata
        }

    def get_user_friendly_message(self) -> str:
        """Get user-friendly error message with suggestions"""
        parts = [f"❌ {self.message}"]

        if self.recovery_suggestions:
            parts.append("\n💡 How to fix this:")
            for i, suggestion in enumerate(self.recovery_suggestions, 1):
                parts.append(f"   {i}. {suggestion}")

        if self.technical_details:
            parts.append(f"\n📋 Technical details: {self.technical_details}")

        return "\n".join(parts)


class NetworkError(KoalasForgeError):
    """Network-related errors"""

    def __init__(self, message: str, url: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.NETWORK,
            recovery_suggestions=[
                "Check your internet connection",
                "Try again in a few moments",
                "Check if the server is accessible",
                "Verify firewall settings"
            ],
            metadata={"url": url} if url else {},
            **kwargs
        )


class PermissionError(KoalasForgeError):
    """Permission-related errors"""

    def __init__(self, message: str, path: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.PERMISSION,
            recovery_suggestions=[
                "Run the installer with administrator/sudo privileges",
                "Check file and directory permissions",
                "Ensure you have write access to the installation directory"
            ],
            metadata={"path": path} if path else {},
            **kwargs
        )


class DependencyError(KoalasForgeError):
    """Missing dependency errors"""

    def __init__(self, message: str, dependency: Optional[str] = None, **kwargs):
        suggestions = kwargs.pop("recovery_suggestions", [])

        if not suggestions and dependency:
            suggestions = [
                f"Install {dependency} first",
                "Check the application requirements",
                "Use the wizard mode to auto-install dependencies"
            ]

        super().__init__(
            message=message,
            category=ErrorCategory.DEPENDENCY,
            recovery_suggestions=suggestions,
            metadata={"dependency": dependency} if dependency else {},
            **kwargs
        )


class PlatformError(KoalasForgeError):
    """Platform compatibility errors"""

    def __init__(self, message: str, platform: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.PLATFORM,
            recovery_suggestions=[
                "Check if this application is available for your platform",
                "Try an alternative application with similar features",
                "Check the application's official website for platform support"
            ],
            metadata={"platform": platform} if platform else {},
            **kwargs
        )


class DiskSpaceError(KoalasForgeError):
    """Insufficient disk space errors"""

    def __init__(self, message: str, required_space: Optional[int] = None, available_space: Optional[int] = None, **kwargs):
        suggestions = [
            "Free up disk space by removing unused files",
            "Install to a different drive with more space",
            "Reduce the number of applications to install"
        ]

        if required_space and available_space:
            required_gb = required_space / (1024**3)
            available_gb = available_space / (1024**3)
            message = f"{message} (Required: {required_gb:.1f}GB, Available: {available_gb:.1f}GB)"

        super().__init__(
            message=message,
            category=ErrorCategory.DISK_SPACE,
            severity=ErrorSeverity.CRITICAL,
            recovery_suggestions=suggestions,
            metadata={
                "required_space": required_space,
                "available_space": available_space
            },
            **kwargs
        )


class PackageManagerError(KoalasForgeError):
    """Package manager errors"""

    def __init__(self, message: str, package_manager: Optional[str] = None, **kwargs):
        suggestions = kwargs.pop("recovery_suggestions", [])

        if not suggestions:
            if package_manager == "brew":
                suggestions = [
                    "Install Homebrew: /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"",
                    "Run 'brew doctor' to fix issues",
                    "Update Homebrew: brew update"
                ]
            elif package_manager == "apt":
                suggestions = [
                    "Update package list: sudo apt update",
                    "Fix broken packages: sudo apt --fix-broken install",
                    "Clear package cache: sudo apt clean"
                ]
            elif package_manager == "winget":
                suggestions = [
                    "Update Windows to the latest version",
                    "Install App Installer from Microsoft Store",
                    "Run 'winget source update' to refresh package lists"
                ]
            else:
                suggestions = [
                    f"Ensure {package_manager} is installed and accessible",
                    "Check package manager documentation",
                    "Try updating the package manager"
                ]

        super().__init__(
            message=message,
            category=ErrorCategory.PACKAGE_MANAGER,
            recovery_suggestions=suggestions,
            metadata={"package_manager": package_manager} if package_manager else {},
            **kwargs
        )


class ChecksumError(KoalasForgeError):
    """Checksum verification errors"""

    def __init__(self, message: str, expected: Optional[str] = None, actual: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.CHECKSUM,
            severity=ErrorSeverity.ERROR,
            recovery_suggestions=[
                "Download the file again (may be corrupted)",
                "Check your internet connection stability",
                "Verify the file source is legitimate",
                "Contact support if the issue persists"
            ],
            metadata={
                "expected_checksum": expected,
                "actual_checksum": actual
            } if expected and actual else {},
            **kwargs
        )


class ConfigurationError(KoalasForgeError):
    """Configuration errors"""

    def __init__(self, message: str, config_file: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.CONFIGURATION,
            recovery_suggestions=[
                "Check the configuration file syntax",
                "Restore default configuration",
                "Refer to the documentation for correct format"
            ],
            metadata={"config_file": config_file} if config_file else {},
            **kwargs
        )


# Error message templates
ERROR_MESSAGES = {
    # Network errors
    "download_failed": "Failed to download {filename}",
    "connection_timeout": "Connection timed out while accessing {url}",
    "connection_refused": "Connection refused by server",

    # Permission errors
    "no_write_permission": "No write permission for {path}",
    "requires_admin": "This operation requires administrator privileges",

    # Dependency errors
    "missing_dependency": "Missing required dependency: {dependency}",
    "incompatible_version": "{app} version {version} is not compatible",

    # Platform errors
    "unsupported_platform": "{app} is not available for {platform}",
    "wsl2_not_detected": "WSL2 not detected. Some features require WSL2.",

    # Disk space errors
    "insufficient_space": "Insufficient disk space",
    "disk_full": "Disk is full",

    # Package manager errors
    "brew_not_found": "Homebrew not found",
    "apt_lock": "Another package manager is running",
    "package_not_found": "Package {package} not found",

    # Checksum errors
    "checksum_mismatch": "File checksum verification failed",

    # Configuration errors
    "invalid_config": "Invalid configuration file",
    "missing_config": "Configuration file not found"
}


def create_error(
    error_key: str,
    category: ErrorCategory = ErrorCategory.UNKNOWN,
    severity: ErrorSeverity = ErrorSeverity.ERROR,
    **kwargs
) -> KoalasForgeError:
    """
    Create an error from a template

    Args:
        error_key: Key in ERROR_MESSAGES
        category: Error category
        severity: Error severity
        **kwargs: Template variables and error parameters

    Returns:
        Appropriate KoalasForgeError subclass
    """
    # Get message template
    message_template = ERROR_MESSAGES.get(error_key, error_key)
    message = message_template.format(**{k: v for k, v in kwargs.items() if not k.startswith('_')})

    # Extract error-specific parameters
    recovery_suggestions = kwargs.get("recovery_suggestions")
    technical_details = kwargs.get("technical_details")

    # Create appropriate error type based on category
    if category == ErrorCategory.NETWORK:
        return NetworkError(
            message=message,
            url=kwargs.get("url"),
            recovery_suggestions=recovery_suggestions,
            technical_details=technical_details
        )
    elif category == ErrorCategory.PERMISSION:
        return PermissionError(
            message=message,
            path=kwargs.get("path"),
            recovery_suggestions=recovery_suggestions,
            technical_details=technical_details
        )
    elif category == ErrorCategory.DEPENDENCY:
        return DependencyError(
            message=message,
            dependency=kwargs.get("dependency"),
            recovery_suggestions=recovery_suggestions,
            technical_details=technical_details
        )
    elif category == ErrorCategory.PLATFORM:
        return PlatformError(
            message=message,
            platform=kwargs.get("platform"),
            recovery_suggestions=recovery_suggestions,
            technical_details=technical_details
        )
    elif category == ErrorCategory.DISK_SPACE:
        return DiskSpaceError(
            message=message,
            required_space=kwargs.get("required_space"),
            available_space=kwargs.get("available_space"),
            recovery_suggestions=recovery_suggestions,
            technical_details=technical_details
        )
    elif category == ErrorCategory.PACKAGE_MANAGER:
        return PackageManagerError(
            message=message,
            package_manager=kwargs.get("package_manager"),
            recovery_suggestions=recovery_suggestions,
            technical_details=technical_details
        )
    elif category == ErrorCategory.CHECKSUM:
        return ChecksumError(
            message=message,
            expected=kwargs.get("expected"),
            actual=kwargs.get("actual"),
            recovery_suggestions=recovery_suggestions,
            technical_details=technical_details
        )
    elif category == ErrorCategory.CONFIGURATION:
        return ConfigurationError(
            message=message,
            config_file=kwargs.get("config_file"),
            recovery_suggestions=recovery_suggestions,
            technical_details=technical_details
        )
    else:
        return KoalasForgeError(
            message=message,
            category=category,
            severity=severity,
            recovery_suggestions=recovery_suggestions or [],
            technical_details=technical_details
        )


# Common error shortcuts
def network_error(message: str, **kwargs) -> NetworkError:
    """Create a network error"""
    return NetworkError(message, **kwargs)


def permission_error(message: str, **kwargs) -> PermissionError:
    """Create a permission error"""
    return PermissionError(message, **kwargs)


def dependency_error(message: str, **kwargs) -> DependencyError:
    """Create a dependency error"""
    return DependencyError(message, **kwargs)


def platform_error(message: str, **kwargs) -> PlatformError:
    """Create a platform error"""
    return PlatformError(message, **kwargs)


if __name__ == "__main__":
    # Test error messages
    print("Testing error messages...\n")

    # Network error
    err = create_error(
        "download_failed",
        category=ErrorCategory.NETWORK,
        filename="python-3.11.pkg",
        url="https://example.com/python.pkg"
    )
    print(err.get_user_friendly_message())
    print("\n" + "="*60 + "\n")

    # Permission error
    err = PermissionError(
        "Cannot write to /usr/local/bin",
        path="/usr/local/bin"
    )
    print(err.get_user_friendly_message())
    print("\n" + "="*60 + "\n")

    # Package manager error
    err = PackageManagerError(
        "Homebrew installation failed",
        package_manager="brew",
        technical_details="Command failed with exit code 1"
    )
    print(err.get_user_friendly_message())
