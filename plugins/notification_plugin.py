"""
🔔 Notification Plugin for Koala's Forge
Sends desktop notifications for installation events

Installation:
  Copy this file to: ~/.koalas-forge/plugins/notification_plugin.py

Requirements:
  macOS: Uses native osascript
  Linux: Uses notify-send (install with: apt install libnotify-bin)
  Windows: Uses win10toast (install with: pip install win10toast)
"""

import subprocess
import platform
from src.core.event_system import Event, EventType


class NotificationPlugin:
    """Sends desktop notifications for installation events"""

    name = "NotificationPlugin"
    version = "1.0.0"
    description = "Desktop notifications for installation events"

    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.system = platform.system()
        print(f"🔔 {self.name} v{self.version} initialized")

    def activate(self):
        """Register event handlers"""
        # Listen to installation events
        self.event_bus.on(EventType.INSTALL_STARTED, self._on_install_started)
        self.event_bus.on(EventType.INSTALL_COMPLETED, self._on_install_completed)
        self.event_bus.on(EventType.INSTALL_FAILED, self._on_install_failed)

        # Listen to download events
        self.event_bus.on(EventType.DOWNLOAD_COMPLETED, self._on_download_completed)

        print(f"  ✓ Registered notification handlers")

    def deactivate(self):
        """Unregister event handlers"""
        # Event bus should handle cleanup
        print(f"  ✓ Deactivated notification handlers")

    def _send_notification(self, title: str, message: str, sound: bool = True):
        """Send a desktop notification"""
        try:
            if self.system == "Darwin":  # macOS
                sound_arg = "sound name \"Glass\"" if sound else ""
                script = f'display notification "{message}" with title "{title}" {sound_arg}'
                subprocess.run(["osascript", "-e", script], check=False)

            elif self.system == "Linux":
                urgency = "normal" if sound else "low"
                subprocess.run([
                    "notify-send",
                    "-u", urgency,
                    title,
                    message
                ], check=False)

            elif self.system == "Windows":
                try:
                    from win10toast import ToastNotifier
                    toaster = ToastNotifier()
                    toaster.show_toast(title, message, duration=5, threaded=True)
                except ImportError:
                    print(f"💡 Install win10toast: pip install win10toast")

        except Exception as e:
            # Fail silently - notifications are not critical
            print(f"  ⚠️  Could not send notification: {e}")

    def _on_install_started(self, event: Event):
        """Handle installation start"""
        app = event.data.get('app', 'Unknown app')
        self._send_notification(
            "🐨 Koala's Forge",
            f"Installing {app}...",
            sound=False
        )

    def _on_install_completed(self, event: Event):
        """Handle installation completion"""
        app = event.data.get('app', 'Unknown app')
        self._send_notification(
            "🐨 Koala's Forge",
            f"✅ {app} installed successfully!",
            sound=True
        )

    def _on_install_failed(self, event: Event):
        """Handle installation failure"""
        app = event.data.get('app', 'Unknown app')
        error = event.data.get('error', 'Unknown error')
        self._send_notification(
            "🐨 Koala's Forge - Error",
            f"❌ Failed to install {app}: {error}",
            sound=True
        )

    def _on_download_completed(self, event: Event):
        """Handle download completion"""
        app = event.data.get('app', 'Unknown app')
        size = event.data.get('size', 'Unknown size')
        self._send_notification(
            "🐨 Koala's Forge",
            f"⬇️  Downloaded {app} ({size})",
            sound=False
        )


# Plugin entry point
def create_plugin(event_bus):
    """Factory function to create plugin instance"""
    return NotificationPlugin(event_bus)
