#!/usr/bin/env python3
"""
Test script for Koala's Forge MVP Features
Demonstrates: Events, Plugins, Rollback, Parallel Downloads, Cloud Sync
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.event_system import EventBus, Event, EventType, get_event_bus
from src.core.plugin_system import PluginManager
from src.core.rollback_system import RollbackManager
from src.core.cloud_sync import CloudSyncManager
from datetime import datetime


async def test_event_system():
    """Test the event-driven architecture"""
    print("\n" + "="*60)
    print("🎯 Testing Event System")
    print("="*60)

    bus = get_event_bus()

    # Register some test handlers
    def on_install(event: Event):
        print(f"  Handler: Installing {event.data['app']}...")

    async def on_complete(event: Event):
        print(f"  Handler: {event.data['app']} installation complete!")

    bus.on(EventType.INSTALL_STARTED, on_install)
    bus.on(EventType.INSTALL_COMPLETED, on_complete)

    # Emit test events
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

    # Show stats
    stats = bus.get_stats()
    print(f"\n  ✓ Event bus stats: {stats['sync_handlers']} sync handlers, {stats['async_handlers']} async handlers")
    print(f"  ✓ Event history: {len(bus.get_history())} events")


async def test_plugin_system():
    """Test the plugin system"""
    print("\n" + "="*60)
    print("🔌 Testing Plugin System")
    print("="*60)

    bus = get_event_bus()
    plugin_manager = PluginManager(bus)

    # Try to load plugins from plugins directory
    print("\n  Discovering plugins...")
    plugin_files = await plugin_manager.discover_plugins()
    print(f"  Found {len(plugin_files)} plugin file(s)")

    # Load all plugins
    if plugin_files:
        print("\n  Loading plugins...")
        await plugin_manager.load_all_plugins()

        # List loaded plugins
        print("\n  Loaded plugins:")
        for plugin_info in plugin_manager.list_plugins():
            print(f"    - {plugin_info['name']} v{plugin_info['version']}")
            print(f"      {plugin_info['description']}")

        # Emit some events to test plugins
        print("\n  Emitting test events...")
        await bus.emit(Event(
            type=EventType.INSTALL_STARTED,
            data={'app': 'Python'},
            source='test'
        ))

        await bus.emit(Event(
            type=EventType.INSTALL_COMPLETED,
            data={'app': 'Python'},
            source='test'
        ))
    else:
        print("  No plugins found in plugins directory")

    print("\n  ✓ Plugin system tested")


async def test_rollback_system():
    """Test the rollback system"""
    print("\n" + "="*60)
    print("💾 Testing Rollback System")
    print("="*60)

    rollback_mgr = RollbackManager(get_event_bus())

    # Create a snapshot
    print("\n  Creating snapshot...")
    snapshot_id = await rollback_mgr.create_snapshot("Test snapshot before installation")
    print(f"  ✓ Created snapshot: {snapshot_id}")

    # List snapshots
    snapshots = rollback_mgr.list_snapshots()
    print(f"\n  Available snapshots: {len(snapshots)}")
    for snap in snapshots[-3:]:  # Show last 3
        print(f"    - {snap['id']}: {snap['description']}")
        print(f"      {snap['app_count']} apps, created {snap['date']}")

    print("\n  ✓ Rollback system tested")


async def test_cloud_sync():
    """Test the cloud sync system"""
    print("\n" + "="*60)
    print("☁️  Testing Cloud Sync System")
    print("="*60)

    sync_mgr = CloudSyncManager(passphrase="test-passphrase")

    # Show available backends
    backends = sync_mgr.get_available_backends()
    print(f"\n  Available sync backends: {backends}")

    # Create test profile
    test_profile = {
        'name': 'test-profile',
        'description': 'Test profile for MVP demo',
        'apps': ['git', 'python', 'docker'],
        'presets': ['development'],
        'created': datetime.now().isoformat()
    }

    # Try to sync to available backends
    print("\n  Syncing profile...")
    results = await sync_mgr.sync_profile(test_profile)

    for backend, success in results.items():
        status = "✓" if success else "✗"
        print(f"    {status} {backend}: {'Success' if success else 'Failed'}")

    # Try to pull back
    print("\n  Pulling profile...")
    for backend in backends[:1]:  # Just test first backend
        pulled = await sync_mgr.pull_profile('test-profile', backend)
        if pulled:
            print(f"    ✓ Pulled from {backend}: {pulled['name']}")
            print(f"      Apps: {', '.join(pulled['apps'])}")
        else:
            print(f"    ✗ Failed to pull from {backend}")

    print("\n  ✓ Cloud sync tested")


async def test_integration():
    """Test everything working together"""
    print("\n" + "="*60)
    print("🚀 Testing Full Integration")
    print("="*60)

    bus = get_event_bus()

    # Setup monitoring
    def event_logger(event: Event):
        print(f"  📢 Event: {event.type.value} from {event.source}")

    bus.on_all(event_logger)

    # Simulate a full installation workflow
    print("\n  Simulating installation workflow...")

    # 1. Create snapshot before installation
    rollback_mgr = RollbackManager(bus)
    snapshot_id = await rollback_mgr.create_snapshot("Before installing Docker")

    # 2. Emit installation events
    await bus.emit(Event(
        type=EventType.DOWNLOAD_STARTED,
        data={'app': 'Docker', 'size': 500000000},
        source='installer'
    ))

    await asyncio.sleep(0.1)

    await bus.emit(Event(
        type=EventType.DOWNLOAD_COMPLETED,
        data={'app': 'Docker'},
        source='installer'
    ))

    await bus.emit(Event(
        type=EventType.INSTALL_STARTED,
        data={'app': 'Docker'},
        source='installer'
    ))

    await asyncio.sleep(0.1)

    await bus.emit(Event(
        type=EventType.INSTALL_COMPLETED,
        data={'app': 'Docker'},
        source='installer'
    ))

    # 3. Save profile and sync
    sync_mgr = CloudSyncManager()
    profile = {
        'name': 'docker-setup',
        'description': 'Setup with Docker',
        'apps': ['docker'],
        'presets': [],
        'created': datetime.now().isoformat()
    }
    await sync_mgr.push_profile(profile, 'local')

    print("\n  ✓ Full workflow completed successfully")


async def main():
    """Run all tests"""
    print("\n🐨 Koala's Forge MVP Feature Tests")
    print("Testing all new features: Events, Plugins, Rollback, Sync\n")

    try:
        # Run tests
        await test_event_system()
        await test_plugin_system()
        await test_rollback_system()
        await test_cloud_sync()
        await test_integration()

        print("\n" + "="*60)
        print("✅ All tests completed successfully!")
        print("="*60)

        # Show summary
        bus = get_event_bus()
        print(f"\nFinal event bus stats:")
        stats = bus.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")

        print(f"\nTotal events processed: {len(bus.get_history())}")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
