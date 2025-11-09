#!/usr/bin/env python3
"""
Example Plugin: Installation Logger
Demonstrates how to create a simple plugin for Koala's Forge
"""

import sys
from pathlib import Path

# Add src to path so we can import
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.plugin_system import Plugin
from src.core.event_system import EventBus, Event, EventType


class InstallationLogger(Plugin):
    """
    Example plugin that logs all installation events to a file
    """

    def __init__(self):
        super().__init__()
        self.name = "InstallationLogger"
        self.version = "1.0.0"
        self.author = "Koala's Forge Team"
        self.description = "Logs all installation events to a file"
        self.log_file = None

    async def on_load(self, event_bus: EventBus, config: dict):
        """Called when plugin is loaded"""
        self.event_bus = event_bus

        # Setup log file
        config_dir = self.get_config_dir()
        self.log_file = config_dir / "installation_log.txt"

        # Write header
        with open(self.log_file, 'a') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"Installation Logger Plugin Started\n")
            f.write(f"{'='*60}\n\n")

        # Register event handlers
        self.register_handler(EventType.INSTALL_STARTED, self.on_install_started)
        self.register_handler(EventType.INSTALL_COMPLETED, self.on_install_completed)
        self.register_handler(EventType.INSTALL_FAILED, self.on_install_failed)
        self.register_handler(EventType.DOWNLOAD_STARTED, self.on_download_started)
        self.register_handler(EventType.DOWNLOAD_COMPLETED, self.on_download_completed)

        self.log_info(f"Logging to: {self.log_file}")

    async def on_unload(self):
        """Called when plugin is unloaded"""
        if self.log_file:
            with open(self.log_file, 'a') as f:
                f.write(f"\n{'='*60}\n")
                f.write(f"Installation Logger Plugin Stopped\n")
                f.write(f"{'='*60}\n\n")

        self.log_info("Plugin unloaded")

    async def on_install_started(self, event: Event):
        """Log when installation starts"""
        app_name = event.data.get('app', 'Unknown')
        timestamp = event.timestamp

        with open(self.log_file, 'a') as f:
            f.write(f"[{timestamp}] 🚀 STARTED: {app_name}\n")

        self.log_debug(f"Logged install start: {app_name}")

    async def on_install_completed(self, event: Event):
        """Log when installation completes"""
        app_name = event.data.get('app', 'Unknown')
        timestamp = event.timestamp

        with open(self.log_file, 'a') as f:
            f.write(f"[{timestamp}] ✅ COMPLETED: {app_name}\n")

        self.log_debug(f"Logged install completion: {app_name}")

    async def on_install_failed(self, event: Event):
        """Log when installation fails"""
        app_name = event.data.get('app', 'Unknown')
        error = event.data.get('error', 'Unknown error')
        timestamp = event.timestamp

        with open(self.log_file, 'a') as f:
            f.write(f"[{timestamp}] ❌ FAILED: {app_name} - {error}\n")

        self.log_debug(f"Logged install failure: {app_name}")

    async def on_download_started(self, event: Event):
        """Log when download starts"""
        app_name = event.data.get('app', 'Unknown')
        timestamp = event.timestamp

        with open(self.log_file, 'a') as f:
            f.write(f"[{timestamp}] 📥 DOWNLOAD STARTED: {app_name}\n")

    async def on_download_completed(self, event: Event):
        """Log when download completes"""
        app_name = event.data.get('app', 'Unknown')
        timestamp = event.timestamp

        with open(self.log_file, 'a') as f:
            f.write(f"[{timestamp}] 📦 DOWNLOAD COMPLETED: {app_name}\n")
