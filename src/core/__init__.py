"""
Koala's Forge Core Modules
"""

from .platform_detection import (
    PlatformDetector,
    PlatformInfo,
    PlatformType,
    Architecture,
    get_platform,
    is_wsl,
    is_wsl2,
    is_macos,
    is_linux,
    is_apple_silicon
)

from .download_manager import (
    DownloadManager,
    DownloadProgress,
    DownloadStatus,
    DownloadTask,
    download_file
)

from .errors import (
    KoalasForgeError,
    ErrorCategory,
    ErrorSeverity,
    NetworkError,
    PermissionError,
    DependencyError,
    PlatformError,
    DiskSpaceError,
    PackageManagerError,
    ChecksumError,
    ConfigurationError,
    create_error
)

__all__ = [
    # Platform detection
    'PlatformDetector',
    'PlatformInfo',
    'PlatformType',
    'Architecture',
    'get_platform',
    'is_wsl',
    'is_wsl2',
    'is_macos',
    'is_linux',
    'is_apple_silicon',

    # Download manager
    'DownloadManager',
    'DownloadProgress',
    'DownloadStatus',
    'DownloadTask',
    'download_file',

    # Errors
    'KoalasForgeError',
    'ErrorCategory',
    'ErrorSeverity',
    'NetworkError',
    'PermissionError',
    'DependencyError',
    'PlatformError',
    'DiskSpaceError',
    'PackageManagerError',
    'ChecksumError',
    'ConfigurationError',
    'create_error',
]

__version__ = '1.1.1'
