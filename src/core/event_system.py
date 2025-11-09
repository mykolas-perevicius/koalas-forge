#!/usr/bin/env python3
"""
Event-Driven Architecture for Koala's Forge
Enables reactive features, plugins, and extensibility
"""

import asyncio
import logging
import time
from enum import Enum
from typing import Callable, Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


class EventType(Enum):
    """All event types in Koala's Forge"""

    # Installation Events
    INSTALL_STARTED = "install.started"
    INSTALL_PROGRESS = "install.progress"
    INSTALL_COMPLETED = "install.completed"
    INSTALL_FAILED = "install.failed"
    INSTALL_PAUSED = "install.paused"
    INSTALL_RESUMED = "install.resumed"
    INSTALL_CANCELLED = "install.cancelled"

    # Download Events
    DOWNLOAD_STARTED = "download.started"
    DOWNLOAD_PROGRESS = "download.progress"
    DOWNLOAD_COMPLETED = "download.completed"
    DOWNLOAD_FAILED = "download.failed"

    # App Events
    APP_DETECTED = "app.detected"
    APP_INSTALLED = "app.installed"
    APP_UPDATED = "app.updated"
    APP_UNINSTALLED = "app.uninstalled"

    # System Events
    SYSTEM_INFO_UPDATED = "system.info_updated"
    NETWORK_CHANGED = "network.changed"
    DISK_SPACE_LOW = "disk.space_low"
    PERMISSION_REQUIRED = "permission.required"

    # Profile Events
    PROFILE_CREATED = "profile.created"
    PROFILE_LOADED = "profile.loaded"
    PROFILE_EXPORTED = "profile.exported"
    PROFILE_IMPORTED = "profile.imported"
    PROFILE_SYNCED = "profile.synced"

    # Rollback Events
    SNAPSHOT_CREATED = "snapshot.created"
    ROLLBACK_INITIATED = "rollback.initiated"
    ROLLBACK_COMPLETED = "rollback.completed"
    ROLLBACK_FAILED = "rollback.failed"

    # Plugin Events
    PLUGIN_LOADED = "plugin.loaded"
    PLUGIN_UNLOADED = "plugin.unloaded"
    PLUGIN_ERROR = "plugin.error"


@dataclass
class Event:
    """Event data structure"""
    type: EventType
    data: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    source: str = "koalas_forge"
    id: Optional[str] = None

    def __post_init__(self):
        if self.id is None:
            self.id = f"{self.type.value}_{int(self.timestamp * 1000)}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            'id': self.id,
            'type': self.type.value,
            'data': self.data,
            'timestamp': self.timestamp,
            'source': self.source
        }


class EventBus:
    """
    Central event bus for Koala's Forge
    Enables decoupled, reactive architecture
    """

    def __init__(self, enable_logging: bool = True):
        self._sync_listeners: Dict[EventType, List[Callable]] = {}
        self._async_listeners: Dict[EventType, List[Callable]] = {}
        self._wildcard_listeners: List[Callable] = []  # Listen to all events
        self._event_queue: asyncio.Queue = asyncio.Queue()
        self._processing_task: Optional[asyncio.Task] = None
        self._enable_logging = enable_logging
        self._event_history: List[Event] = []  # For debugging
        self._max_history = 1000

        logger.info("🎯 EventBus initialized")

    def on(self, event_type: EventType, handler: Callable, priority: int = 0):
        """
        Register event handler

        Args:
            event_type: Type of event to listen for
            handler: Callback function (sync or async)
            priority: Higher priority handlers run first (default: 0)
        """
        if asyncio.iscoroutinefunction(handler):
            listeners = self._async_listeners.setdefault(event_type, [])
        else:
            listeners = self._sync_listeners.setdefault(event_type, [])

        listeners.append((priority, handler))
        listeners.sort(key=lambda x: x[0], reverse=True)  # Sort by priority

        logger.debug(f"Registered handler for {event_type.value}")

    def on_all(self, handler: Callable):
        """Register handler for all events (useful for logging, debugging)"""
        self._wildcard_listeners.append(handler)
        logger.debug("Registered wildcard handler")

    def off(self, event_type: EventType, handler: Callable):
        """Unregister event handler"""
        # Remove from sync listeners
        if event_type in self._sync_listeners:
            self._sync_listeners[event_type] = [
                (p, h) for p, h in self._sync_listeners[event_type] if h != handler
            ]

        # Remove from async listeners
        if event_type in self._async_listeners:
            self._async_listeners[event_type] = [
                (p, h) for p, h in self._async_listeners[event_type] if h != handler
            ]

        logger.debug(f"Unregistered handler for {event_type.value}")

    async def emit(self, event: Event):
        """
        Emit event to all registered listeners

        Args:
            event: Event to emit
        """
        if self._enable_logging:
            logger.info(f"📢 Event: {event.type.value} from {event.source}")
            self._event_history.append(event)
            if len(self._event_history) > self._max_history:
                self._event_history.pop(0)

        # Call wildcard listeners first
        for handler in self._wildcard_listeners:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                logger.error(f"Wildcard handler error: {e}")

        # Call sync handlers
        for priority, handler in self._sync_listeners.get(event.type, []):
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Sync handler error for {event.type.value}: {e}")

        # Call async handlers
        tasks = []
        for priority, handler in self._async_listeners.get(event.type, []):
            tasks.append(self._safe_handler_call(handler, event))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _safe_handler_call(self, handler: Callable, event: Event):
        """Safely call async handler with error handling"""
        try:
            await handler(event)
        except Exception as e:
            logger.error(f"Async handler error for {event.type.value}: {e}")
            # Emit error event
            await self.emit(Event(
                type=EventType.PLUGIN_ERROR,
                data={'error': str(e), 'handler': handler.__name__},
                source='event_bus'
            ))

    async def emit_and_wait(self, event: Event, timeout: float = 10.0) -> bool:
        """
        Emit event and wait for all handlers to complete

        Args:
            event: Event to emit
            timeout: Maximum time to wait (seconds)

        Returns:
            True if all handlers completed, False if timeout
        """
        try:
            await asyncio.wait_for(self.emit(event), timeout=timeout)
            return True
        except asyncio.TimeoutError:
            logger.warning(f"Event {event.type.value} handlers timed out after {timeout}s")
            return False

    def emit_sync(self, event: Event):
        """Synchronous emit (only calls sync handlers)"""
        for priority, handler in self._sync_listeners.get(event.type, []):
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Sync handler error: {e}")

    async def start_processing(self):
        """Start background event processing loop"""
        if self._processing_task is None:
            self._processing_task = asyncio.create_task(self._process_events())
            logger.info("🚀 Event processing started")

    async def stop_processing(self):
        """Stop background event processing"""
        if self._processing_task:
            self._processing_task.cancel()
            try:
                await self._processing_task
            except asyncio.CancelledError:
                pass
            self._processing_task = None
            logger.info("⏹️  Event processing stopped")

    async def _process_events(self):
        """Background event processing loop"""
        while True:
            try:
                event = await self._event_queue.get()
                await self.emit(event)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Event processing error: {e}")

    def get_history(self, event_type: Optional[EventType] = None, limit: int = 100) -> List[Event]:
        """
        Get event history (useful for debugging)

        Args:
            event_type: Filter by event type (optional)
            limit: Maximum number of events to return

        Returns:
            List of events
        """
        events = self._event_history

        if event_type:
            events = [e for e in events if e.type == event_type]

        return events[-limit:]

    def clear_history(self):
        """Clear event history"""
        self._event_history.clear()
        logger.debug("Event history cleared")

    def get_stats(self) -> Dict[str, Any]:
        """Get event bus statistics"""
        return {
            'sync_handlers': sum(len(handlers) for handlers in self._sync_listeners.values()),
            'async_handlers': sum(len(handlers) for handlers in self._async_listeners.values()),
            'wildcard_handlers': len(self._wildcard_listeners),
            'event_history_size': len(self._event_history),
            'processing': self._processing_task is not None
        }


# Global event bus instance
_global_event_bus: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """Get global event bus instance"""
    global _global_event_bus
    if _global_event_bus is None:
        _global_event_bus = EventBus()
    return _global_event_bus


# Example usage
if __name__ == "__main__":
    async def example():
        bus = EventBus()

        # Register handlers
        bus.on(EventType.INSTALL_STARTED, lambda e: print(f"Installing {e.data['app']}..."))
        bus.on(EventType.INSTALL_COMPLETED, lambda e: print(f"✓ {e.data['app']} installed!"))

        # Emit events
        await bus.emit(Event(
            type=EventType.INSTALL_STARTED,
            data={'app': 'Docker'},
            source='test'
        ))

        await bus.emit(Event(
            type=EventType.INSTALL_COMPLETED,
            data={'app': 'Docker'},
            source='test'
        ))

        # Show stats
        print(f"\nStats: {bus.get_stats()}")
        print(f"History: {len(bus.get_history())} events")

    asyncio.run(example())
