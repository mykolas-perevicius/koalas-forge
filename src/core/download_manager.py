#!/usr/bin/env python3
"""
Download Manager with Resume Capability
Implements HTTP range requests and .part file handling for interrupted downloads
"""

import asyncio
import hashlib
import logging
import os
import shutil
import weakref
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, Callable, Dict, Any, Set
from urllib.parse import urlparse

try:
    import aiohttp
    import aiofiles
except ImportError:
    import subprocess
    import sys
    print("Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "aiohttp", "aiofiles"])
    import aiohttp
    import aiofiles


logger = logging.getLogger(__name__)


class DownloadStatus(Enum):
    """Download status states"""
    PENDING = "pending"
    DOWNLOADING = "downloading"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class DownloadProgress:
    """Download progress information"""
    url: str
    dest_path: Path
    total_size: int = 0
    downloaded_size: int = 0
    status: DownloadStatus = DownloadStatus.PENDING
    speed: float = 0.0  # bytes per second
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error: Optional[str] = None
    checksum: Optional[str] = None
    checksum_type: str = "sha256"

    @property
    def progress_percent(self) -> float:
        """Calculate download progress percentage"""
        if self.total_size == 0:
            return 0.0
        return (self.downloaded_size / self.total_size) * 100

    @property
    def is_resumable(self) -> bool:
        """Check if download can be resumed"""
        return self.downloaded_size > 0 and self.total_size > 0

    @property
    def eta_seconds(self) -> Optional[float]:
        """Estimate time remaining in seconds"""
        if self.speed == 0 or self.total_size == 0:
            return None
        remaining = self.total_size - self.downloaded_size
        return remaining / self.speed


@dataclass
class DownloadTask:
    """Individual download task"""
    id: str
    url: str
    dest_path: Path
    progress: DownloadProgress = field(default_factory=lambda: None)
    checksum: Optional[str] = None
    checksum_type: str = "sha256"
    max_retries: int = 3
    retry_count: int = 0
    chunk_size: int = 8192
    _callbacks: Set = field(default_factory=set)

    def __post_init__(self):
        if self.progress is None:
            self.progress = DownloadProgress(
                url=self.url,
                dest_path=self.dest_path,
                checksum=self.checksum,
                checksum_type=self.checksum_type
            )


class DownloadManager:
    """
    Download manager with resume capability and weak reference callbacks

    CRITICAL FIX: Uses weak references for callbacks to prevent memory leaks
    """

    def __init__(self, max_concurrent: int = 5, download_dir: Optional[Path] = None):
        """
        Initialize download manager

        Args:
            max_concurrent: Maximum number of concurrent downloads
            download_dir: Default download directory
        """
        self.max_concurrent = max_concurrent
        self.download_dir = download_dir or Path.home() / "Downloads" / "koalas-forge"
        self.download_dir.mkdir(parents=True, exist_ok=True)

        # Active downloads
        self.downloads: Dict[str, DownloadTask] = {}
        self.session: Optional[aiohttp.ClientSession] = None

        # Semaphore for limiting concurrent downloads
        self.semaphore = asyncio.Semaphore(max_concurrent)

        # Global progress callbacks (using weak references)
        self._progress_callbacks: Set[weakref.ref] = set()

        logger.info(f"DownloadManager initialized: max_concurrent={max_concurrent}, dir={self.download_dir}")

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
            self.session = None

    def add_progress_callback(self, callback: Callable[[DownloadProgress], None]):
        """
        Add a progress callback using weak reference

        CRITICAL FIX: Uses weak references to prevent memory leaks
        """
        # Create weak reference to callback
        if hasattr(callback, '__self__'):
            # Bound method - create weak reference to the object
            weak_callback = weakref.WeakMethod(callback)
        else:
            # Function - create weak reference
            weak_callback = weakref.ref(callback)

        self._progress_callbacks.add(weak_callback)

    def remove_progress_callback(self, callback: Callable[[DownloadProgress], None]):
        """Remove a progress callback"""
        to_remove = []
        for weak_callback in self._progress_callbacks:
            cb = weak_callback()
            if cb is None or cb == callback:
                to_remove.append(weak_callback)

        for weak_callback in to_remove:
            self._progress_callbacks.discard(weak_callback)

    def _notify_progress(self, progress: DownloadProgress):
        """Notify all progress callbacks"""
        # Clean up dead references and call alive ones
        dead_refs = set()

        for weak_callback in self._progress_callbacks:
            callback = weak_callback()
            if callback is None:
                # Reference is dead, mark for removal
                dead_refs.add(weak_callback)
            else:
                try:
                    callback(progress)
                except Exception as e:
                    logger.error(f"Error in progress callback: {e}")

        # Remove dead references
        self._progress_callbacks -= dead_refs

    async def download(
        self,
        url: str,
        dest_path: Optional[Path] = None,
        checksum: Optional[str] = None,
        checksum_type: str = "sha256",
        resume: bool = True,
        progress_callback: Optional[Callable[[DownloadProgress], None]] = None
    ) -> Path:
        """
        Download a file with resume support

        Args:
            url: URL to download
            dest_path: Destination file path
            checksum: Expected checksum
            checksum_type: Type of checksum (md5, sha1, sha256)
            resume: Whether to resume partial downloads
            progress_callback: Callback for progress updates

        Returns:
            Path to downloaded file

        CRITICAL FIX: Implements HTTP range requests and .part file handling
        """
        if not self.session:
            raise RuntimeError("DownloadManager not initialized. Use async with context manager.")

        # Generate download ID
        download_id = hashlib.md5(url.encode()).hexdigest()

        # Determine destination path
        if dest_path is None:
            filename = Path(urlparse(url).path).name or f"download_{download_id}"
            dest_path = self.download_dir / filename

        dest_path = Path(dest_path)
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        # Create download task
        task = DownloadTask(
            id=download_id,
            url=url,
            dest_path=dest_path,
            checksum=checksum,
            checksum_type=checksum_type
        )

        # Add task-specific callback if provided
        if progress_callback:
            task._callbacks.add(weakref.ref(progress_callback))

        self.downloads[download_id] = task

        # Use semaphore to limit concurrent downloads
        async with self.semaphore:
            try:
                result = await self._download_file(task, resume=resume)
                return result
            except Exception as e:
                logger.error(f"Download failed for {url}: {e}")
                task.progress.status = DownloadStatus.FAILED
                task.progress.error = str(e)
                self._notify_progress(task.progress)
                raise
            finally:
                # Clean up task callbacks
                task._callbacks.clear()

    async def _download_file(self, task: DownloadTask, resume: bool = True) -> Path:
        """
        Internal download implementation with resume support
        """
        part_file = task.dest_path.with_suffix(task.dest_path.suffix + ".part")

        # Check if file already exists and is complete
        if task.dest_path.exists():
            if task.checksum:
                if await self._verify_checksum(task.dest_path, task.checksum, task.checksum_type):
                    logger.info(f"File already exists and verified: {task.dest_path}")
                    task.progress.status = DownloadStatus.COMPLETED
                    task.progress.downloaded_size = task.dest_path.stat().st_size
                    task.progress.total_size = task.progress.downloaded_size
                    self._notify_progress(task.progress)
                    return task.dest_path
            else:
                logger.info(f"File already exists: {task.dest_path}")
                task.progress.status = DownloadStatus.COMPLETED
                return task.dest_path

        # Check for partial download
        existing_size = 0
        if resume and part_file.exists():
            existing_size = part_file.stat().st_size
            logger.info(f"Found partial download: {existing_size} bytes")
            task.progress.downloaded_size = existing_size

        # Prepare headers for resume
        headers = {}
        if existing_size > 0 and resume:
            headers["Range"] = f"bytes={existing_size}-"
            logger.info(f"Resuming download from byte {existing_size}")

        # Start download
        task.progress.status = DownloadStatus.DOWNLOADING
        task.progress.start_time = datetime.now()
        self._notify_progress(task.progress)

        try:
            async with self.session.get(task.url, headers=headers) as response:
                # Check if resume is supported
                if existing_size > 0 and response.status != 206:
                    logger.warning("Server doesn't support resume, starting from beginning")
                    existing_size = 0
                    task.progress.downloaded_size = 0
                    if part_file.exists():
                        part_file.unlink()

                # Get total size
                if response.status == 206:
                    # Partial content
                    content_range = response.headers.get("Content-Range", "")
                    if content_range:
                        total_size = int(content_range.split("/")[1])
                    else:
                        total_size = existing_size + int(response.headers.get("Content-Length", 0))
                else:
                    # Full content
                    total_size = int(response.headers.get("Content-Length", 0))

                task.progress.total_size = total_size

                # Download chunks
                mode = "ab" if existing_size > 0 else "wb"
                async with aiofiles.open(part_file, mode) as f:
                    last_update = datetime.now()
                    async for chunk in response.content.iter_chunked(task.chunk_size):
                        await f.write(chunk)
                        task.progress.downloaded_size += len(chunk)

                        # Update progress every 0.5 seconds
                        now = datetime.now()
                        if (now - last_update).total_seconds() >= 0.5:
                            # Calculate speed
                            elapsed = (now - task.progress.start_time).total_seconds()
                            if elapsed > 0:
                                task.progress.speed = task.progress.downloaded_size / elapsed

                            self._notify_progress(task.progress)
                            last_update = now

            # Download complete, verify and move file
            if task.checksum:
                if not await self._verify_checksum(part_file, task.checksum, task.checksum_type):
                    raise ValueError(f"Checksum verification failed for {task.url}")

            # Move from .part to final destination
            shutil.move(str(part_file), str(task.dest_path))

            # Update status
            task.progress.status = DownloadStatus.COMPLETED
            task.progress.end_time = datetime.now()
            self._notify_progress(task.progress)

            logger.info(f"Download completed: {task.dest_path}")
            return task.dest_path

        except asyncio.CancelledError:
            task.progress.status = DownloadStatus.CANCELLED
            self._notify_progress(task.progress)
            logger.info(f"Download cancelled: {task.url}")
            raise

        except Exception as e:
            task.progress.status = DownloadStatus.FAILED
            task.progress.error = str(e)
            task.progress.end_time = datetime.now()
            self._notify_progress(task.progress)
            raise

    async def _verify_checksum(self, file_path: Path, expected: str, checksum_type: str = "sha256") -> bool:
        """Verify file checksum"""
        try:
            if checksum_type == "md5":
                hasher = hashlib.md5()
            elif checksum_type == "sha1":
                hasher = hashlib.sha1()
            elif checksum_type == "sha256":
                hasher = hashlib.sha256()
            else:
                logger.warning(f"Unknown checksum type: {checksum_type}")
                return True

            async with aiofiles.open(file_path, "rb") as f:
                while chunk := await f.read(8192):
                    hasher.update(chunk)

            actual = hasher.hexdigest()
            matches = actual.lower() == expected.lower()

            if not matches:
                logger.error(f"Checksum mismatch: expected {expected}, got {actual}")

            return matches

        except Exception as e:
            logger.error(f"Error verifying checksum: {e}")
            return False

    async def pause_download(self, download_id: str):
        """Pause a download"""
        task = self.downloads.get(download_id)
        if task:
            task.progress.status = DownloadStatus.PAUSED
            self._notify_progress(task.progress)

    async def cancel_download(self, download_id: str):
        """Cancel a download"""
        task = self.downloads.get(download_id)
        if task:
            task.progress.status = DownloadStatus.CANCELLED
            self._notify_progress(task.progress)

    def get_progress(self, download_id: str) -> Optional[DownloadProgress]:
        """Get download progress"""
        task = self.downloads.get(download_id)
        return task.progress if task else None

    def clear_completed(self):
        """Clear completed downloads from memory"""
        to_remove = [
            download_id
            for download_id, task in self.downloads.items()
            if task.progress.status in (DownloadStatus.COMPLETED, DownloadStatus.FAILED, DownloadStatus.CANCELLED)
        ]

        for download_id in to_remove:
            task = self.downloads[download_id]
            # Clear callbacks to ensure cleanup
            task._callbacks.clear()
            del self.downloads[download_id]

        logger.info(f"Cleared {len(to_remove)} completed downloads")


# Convenience function
async def download_file(
    url: str,
    dest_path: Optional[Path] = None,
    checksum: Optional[str] = None,
    resume: bool = True,
    progress_callback: Optional[Callable[[DownloadProgress], None]] = None
) -> Path:
    """
    Download a single file

    Args:
        url: URL to download
        dest_path: Destination path
        checksum: Expected SHA256 checksum
        resume: Whether to resume partial downloads
        progress_callback: Progress callback function

    Returns:
        Path to downloaded file
    """
    async with DownloadManager() as manager:
        return await manager.download(
            url=url,
            dest_path=dest_path,
            checksum=checksum,
            resume=resume,
            progress_callback=progress_callback
        )


if __name__ == "__main__":
    # Test download with resume
    async def test_download():
        def progress_callback(progress: DownloadProgress):
            print(f"Progress: {progress.progress_percent:.1f}% - {progress.downloaded_size}/{progress.total_size} bytes")

        async with DownloadManager() as manager:
            manager.add_progress_callback(progress_callback)

            # Test download
            test_url = "https://nodejs.org/dist/v20.11.0/node-v20.11.0.pkg"
            result = await manager.download(test_url, resume=True)
            print(f"Downloaded to: {result}")

    # Run test
    # asyncio.run(test_download())
    print("Download manager ready. Import and use with asyncio.run()")
