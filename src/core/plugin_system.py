#!/usr/bin/env python3
"""
Plugin System for Koala's Forge
Enables extensibility and third-party integrations
"""

import asyncio
import importlib.util
import inspect
import logging
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Any

from .event_system import EventBus, Event, EventType, get_event_bus

logger = logging.getLogger(__name__)


class Plugin(ABC):
    """
    Base class for all plugins

    Plugins can:
    - Listen to events
    - Modify installation behavior
    - Add new package sources
    - Integrate with external services
    """

    def __init__(self):
        self.name: str = self.__class__.__name__
        self.version: str = "1.0.0"
        self.author: str = "Unknown"
        self.description: str = "No description provided"
        self.event_bus: Optional[EventBus] = None
        self._registered_handlers: List[tuple] = []

    @abstractmethod
    async def on_load(self, event_bus: EventBus, config: Dict[str, Any]):
        """
        Called when plugin is loaded

        Args:
            event_bus: Global event bus
            config: Plugin configuration from config file
        """
        pass

    @abstractmethod
    async def on_unload(self):
        """
        Called when plugin is unloaded
        Clean up resources here
        """
        pass

    def register_handler(self, event_type: EventType, handler):
        """Helper to register event handler and track it"""
        if self.event_bus:
            self.event_bus.on(event_type, handler)
            self._registered_handlers.append((event_type, handler))

    async def emit_event(self, event: Event):
        """Helper to emit events"""
        if self.event_bus:
            await self.event_bus.emit(event)

    def get_config_dir(self) -> Path:
        """Get plugin's configuration directory"""
        config_dir = Path.home() / ".koalas-forge" / "plugins" / self.name
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir

    def log_info(self, message: str):
        """Log info message"""
        logger.info(f"[{self.name}] {message}")

    def log_error(self, message: str):
        """Log error message"""
        logger.error(f"[{self.name}] {message}")

    def log_debug(self, message: str):
        """Log debug message"""
        logger.debug(f"[{self.name}] {message}")


class PluginManager:
    """
    Manages plugin lifecycle and loading
    """

    def __init__(self, event_bus: Optional[EventBus] = None):
        self.event_bus = event_bus or get_event_bus()
        self.plugins: Dict[str, Plugin] = {}
        self.plugin_dir = Path.home() / ".koalas-forge" / "plugins"
        self.plugin_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"🔌 Plugin directory: {self.plugin_dir}")

    async def discover_plugins(self) -> List[Path]:
        """
        Discover available plugins in plugin directory

        Returns:
            List of plugin file paths
        """
        plugin_files = []

        # Look for .py files
        for plugin_file in self.plugin_dir.glob("*.py"):
            if not plugin_file.name.startswith("_"):
                plugin_files.append(plugin_file)

        # Look for plugin directories with __init__.py
        for plugin_dir in self.plugin_dir.iterdir():
            if plugin_dir.is_dir() and not plugin_dir.name.startswith("_"):
                init_file = plugin_dir / "__init__.py"
                if init_file.exists():
                    plugin_files.append(init_file)

        logger.info(f"Found {len(plugin_files)} plugin(s)")
        return plugin_files

    async def load_plugin(self, plugin_path: Path, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Load a single plugin

        Args:
            plugin_path: Path to plugin file
            config: Optional plugin configuration

        Returns:
            True if loaded successfully
        """
        try:
            # Load module
            module_name = f"koalas_forge_plugin_{plugin_path.stem}"
            spec = importlib.util.spec_from_file_location(module_name, plugin_path)

            if spec is None or spec.loader is None:
                logger.error(f"Failed to load plugin spec: {plugin_path}")
                return False

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            # Find Plugin class
            plugin_class = None
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and
                    issubclass(obj, Plugin) and
                    obj is not Plugin):
                    plugin_class = obj
                    break

            if plugin_class is None:
                logger.error(f"No Plugin class found in {plugin_path}")
                return False

            # Instantiate plugin
            plugin = plugin_class()
            plugin.event_bus = self.event_bus

            # Load plugin
            await plugin.on_load(self.event_bus, config or {})

            # Register plugin
            self.plugins[plugin.name] = plugin

            # Emit event
            await self.event_bus.emit(Event(
                type=EventType.PLUGIN_LOADED,
                data={
                    'name': plugin.name,
                    'version': plugin.version,
                    'author': plugin.author
                },
                source='plugin_manager'
            ))

            logger.info(f"✅ Loaded plugin: {plugin.name} v{plugin.version}")
            return True

        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_path}: {e}")
            await self.event_bus.emit(Event(
                type=EventType.PLUGIN_ERROR,
                data={'plugin': str(plugin_path), 'error': str(e)},
                source='plugin_manager'
            ))
            return False

    async def unload_plugin(self, plugin_name: str) -> bool:
        """
        Unload a plugin

        Args:
            plugin_name: Name of plugin to unload

        Returns:
            True if unloaded successfully
        """
        if plugin_name not in self.plugins:
            logger.warning(f"Plugin not loaded: {plugin_name}")
            return False

        try:
            plugin = self.plugins[plugin_name]

            # Unregister event handlers
            for event_type, handler in plugin._registered_handlers:
                self.event_bus.off(event_type, handler)

            # Call plugin cleanup
            await plugin.on_unload()

            # Remove from registry
            del self.plugins[plugin_name]

            # Emit event
            await self.event_bus.emit(Event(
                type=EventType.PLUGIN_UNLOADED,
                data={'name': plugin_name},
                source='plugin_manager'
            ))

            logger.info(f"🔌 Unloaded plugin: {plugin_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to unload plugin {plugin_name}: {e}")
            return False

    async def load_all_plugins(self):
        """Discover and load all available plugins"""
        plugin_files = await self.discover_plugins()

        for plugin_file in plugin_files:
            await self.load_plugin(plugin_file)

    async def reload_plugin(self, plugin_name: str) -> bool:
        """
        Reload a plugin (unload and load again)

        Args:
            plugin_name: Name of plugin to reload

        Returns:
            True if reloaded successfully
        """
        if plugin_name not in self.plugins:
            logger.warning(f"Plugin not loaded: {plugin_name}")
            return False

        # Find original file path (would need to track this)
        # For now, just unload
        await self.unload_plugin(plugin_name)

        logger.info(f"🔄 Reloaded plugin: {plugin_name}")
        return True

    def get_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """Get loaded plugin by name"""
        return self.plugins.get(plugin_name)

    def list_plugins(self) -> List[Dict[str, Any]]:
        """List all loaded plugins"""
        return [
            {
                'name': plugin.name,
                'version': plugin.version,
                'author': plugin.author,
                'description': plugin.description
            }
            for plugin in self.plugins.values()
        ]

    async def shutdown(self):
        """Shutdown plugin manager and unload all plugins"""
        logger.info("Shutting down plugin manager...")

        for plugin_name in list(self.plugins.keys()):
            await self.unload_plugin(plugin_name)

        logger.info("✅ Plugin manager shut down")


# Example plugin for demonstration
class ExampleLoggerPlugin(Plugin):
    """
    Example plugin that logs all installation events
    """

    def __init__(self):
        super().__init__()
        self.name = "InstallLogger"
        self.version = "1.0.0"
        self.author = "Koala's Forge Team"
        self.description = "Logs all installation events to file"

    async def on_load(self, event_bus: EventBus, config: Dict[str, Any]):
        """Setup event handlers"""
        self.event_bus = event_bus
        self.log_file = self.get_config_dir() / "install_log.txt"

        # Register handlers
        self.register_handler(EventType.INSTALL_STARTED, self.on_install_started)
        self.register_handler(EventType.INSTALL_COMPLETED, self.on_install_completed)
        self.register_handler(EventType.INSTALL_FAILED, self.on_install_failed)

        self.log_info("Logger plugin loaded")

    async def on_unload(self):
        """Cleanup"""
        self.log_info("Logger plugin unloaded")

    async def on_install_started(self, event: Event):
        """Log installation start"""
        app_name = event.data.get('app', 'Unknown')
        with open(self.log_file, 'a') as f:
            f.write(f"[{event.timestamp}] STARTED: {app_name}\n")

    async def on_install_completed(self, event: Event):
        """Log installation completion"""
        app_name = event.data.get('app', 'Unknown')
        with open(self.log_file, 'a') as f:
            f.write(f"[{event.timestamp}] COMPLETED: {app_name}\n")

    async def on_install_failed(self, event: Event):
        """Log installation failure"""
        app_name = event.data.get('app', 'Unknown')
        error = event.data.get('error', 'Unknown error')
        with open(self.log_file, 'a') as f:
            f.write(f"[{event.timestamp}] FAILED: {app_name} - {error}\n")


# Example usage
if __name__ == "__main__":
    async def example():
        # Create event bus and plugin manager
        bus = get_event_bus()
        plugin_manager = PluginManager(bus)

        # Load example plugin programmatically
        example_plugin = ExampleLoggerPlugin()
        await example_plugin.on_load(bus, {})
        plugin_manager.plugins[example_plugin.name] = example_plugin

        # Emit some test events
        await bus.emit(Event(
            type=EventType.INSTALL_STARTED,
            data={'app': 'Docker'},
            source='test'
        ))

        await asyncio.sleep(0.1)

        await bus.emit(Event(
            type=EventType.INSTALL_COMPLETED,
            data={'app': 'Docker'},
            source='test'
        ))

        # List plugins
        print("\nLoaded plugins:")
        for plugin_info in plugin_manager.list_plugins():
            print(f"  - {plugin_info['name']} v{plugin_info['version']}")

        # Shutdown
        await plugin_manager.shutdown()

    asyncio.run(example())
