# 🐨 Koala's Forge CLI Guide

Complete guide to using the `koala` command-line interface.

## Quick Start

```bash
# Make sure you're in the project directory
cd app-installer

# Check CLI version
./koala version

# View system status
./koala status

# Get help
./koala --help
```

## Installation Commands

### Install Applications

```bash
# Install single app
./koala install git

# Install multiple apps
./koala install git docker python

# Install with auto-confirm
./koala install git docker -y
```

**What happens:**
- Automatically creates a rollback snapshot
- Emits events through the event system
- Tracks installation in statistics (if plugin enabled)
- Sends notifications (if plugin enabled)

## Rollback System

### List Snapshots

```bash
./koala rollback list
```

**Output:**
```
📸 Rollback Snapshots (3)

ID                        Date                 Apps       Description
================================================================================
snapshot_1762731259       2025-11-09 18:34     15         Before installing Docker
snapshot_1762731261       2025-11-09 18:35     18         System backup
snapshot_1762731300       2025-11-09 18:40     18         Before mass update
```

### Create Snapshot

```bash
# Create a named snapshot
./koala rollback create "Before major changes"
```

**Output:**
```
✅ Created snapshot: snapshot_1762734177
   Description: Before major changes
   Apps tracked: 42
```

### Restore from Snapshot

```bash
# Restore to a specific snapshot
./koala rollback restore snapshot_1762731259
```

**Output:**
```
🔄 Restoring to snapshot: snapshot_1762731259
✅ Rollback successful!
   Removed: 3 apps
   Added: 0 apps

   Removed apps:
     - docker
     - kubernetes
     - helm
```

## Plugin Management

### List Loaded Plugins

```bash
./koala plugin list
```

**Output:**
```
🔌 Loaded Plugins (4)

Name                      Version    Status
============================================================
InstallationLogger        1.0.0      ✅ Active
NotificationPlugin        1.0.0      ✅ Active
StatisticsPlugin          1.0.0      ✅ Active
AutoUpdatePlugin          1.0.0      ✅ Active
```

### Load a Plugin

```bash
# Load plugin from file
./koala plugin load /path/to/my_plugin.py
```

### Reload a Plugin

```bash
# Reload plugin (useful for development)
./koala plugin reload NotificationPlugin
```

## Cloud Sync

### Check Sync Status

```bash
./koala sync status
```

**Output:**
```
☁️  Cloud Sync Status

Backend: icloud
Enabled: ✅ Yes
Last sync: Never
Sync path: /Users/myko/Library/Mobile Documents/com~apple~CloudDocs/KoalasForge
```

### Push Profile to Cloud

```bash
./koala sync push
```

Pushes your current app configuration to cloud storage (iCloud, Dropbox, etc.)

### Pull Profile from Cloud

```bash
./koala sync pull
```

Pulls the latest profile from cloud storage.

## Event Monitoring

### View Recent Events

```bash
# Show last 20 events
./koala events

# Show last 50 events
./koala events -n 50
```

**Output:**
```
📋 Recent Events (last 6)

Time                 Type                           Source
======================================================================
19:30:45             INSTALL_STARTED                cli
19:30:46             INSTALL_COMPLETED              cli
19:30:46             INSTALL_STARTED                cli
19:30:47             INSTALL_COMPLETED              cli
```

## System Status

### View Full System Status

```bash
./koala status
```

**Output:**
```
🐨 Koala's Forge System Status

Version: 1.2.0

Event System:
  Handlers: 12 sync, 4 async
  Events processed: 143

Plugins:
  Loaded: 4

Rollback:
  Snapshots: 8

Cloud Sync:
  Backend: icloud
  Enabled: True
```

### Diagnose and Fix Issues

```bash
# Check for common issues
./koala doctor

# Automatically fix detected issues
./koala doctor --fix
```

**What it checks:**
- Homebrew installation (macOS)
- Plugin directory exists
- Cache directory exists
- Configuration file exists
- Too many rollback snapshots (>50)
- Package database loaded
- Koala script executable permissions

**Auto-fixes available:**
- Installs Homebrew if missing
- Creates missing directories
- Creates default config file
- Fixes script permissions

### Clean Up Old Snapshots

```bash
# Preview what would be deleted (keeps most recent 10)
./koala cleanup --dry-run

# Clean up, keeping most recent 10 snapshots
./koala cleanup

# Clean up, keeping most recent 20 snapshots
./koala cleanup --keep 20
```

**What happens:**
- Sorts snapshots by timestamp
- Keeps the N most recent snapshots
- Deletes older snapshots
- Frees up disk space

### Force Reinstall Packages

```bash
# Reinstall a package even if already installed
./koala install git --force

# Reinstall multiple packages
./koala install git docker --force

# Test reinstall (dry-run)
./koala install python --force --dry-run
```

**When to use:**
- Package is corrupted
- Need to reset package configuration
- Testing installation process
- Downgrade not working properly

## Plugin Usage Examples

### Installation Logger Plugin

Automatically logs all installation events to a file.

**Location:** `~/.koalas-forge/plugins/installation_log.txt`

**Sample output:**
```
============================================================
Installation Logger Plugin Started
============================================================

[2025-11-09T19:30:45] 🚀 STARTED: git
[2025-11-09T19:30:47] ✅ COMPLETED: git
[2025-11-09T19:30:48] 🚀 STARTED: docker
[2025-11-09T19:30:52] ✅ COMPLETED: docker
```

### Statistics Plugin

Tracks installation statistics and generates reports.

**Usage:**
```python
# In Python REPL or script:
from src.core.event_system import get_event_bus
from plugins.statistics_plugin import StatisticsPlugin

bus = get_event_bus()
stats = StatisticsPlugin(bus)
stats.activate()

# After some installations...
print(stats.get_report())
```

**Sample report:**
```
============================================================
📊 Koala's Forge - Installation Statistics
============================================================

Global Statistics:
  Total installations: 47
  Successful: 45
  Failed: 2
  Success rate: 95.7%

Most Installed Apps:
  git: 12 installs, 3.2s avg
  docker: 8 installs, 45.1s avg
  python: 7 installs, 12.3s avg
  vscode: 6 installs, 8.9s avg
  kubernetes: 4 installs, 67.2s avg

Download Statistics:
  Total downloads: 45
  Total data: 8.47 GB
============================================================
```

### Notification Plugin

Sends desktop notifications for installation events.

**Features:**
- ✅ Notifications when installs start
- ✅ Success notifications with sound
- ✅ Error notifications
- ✅ Download completion notifications

**Platforms:**
- macOS: Native osascript notifications
- Linux: Uses notify-send
- Windows: Uses win10toast

### Auto Update Plugin

Automatically checks for application updates.

**Configuration:** `~/.koalas-forge/auto_update_config.json`

**Sample config:**
```json
{
  "enabled": true,
  "check_on_startup": true,
  "check_interval_hours": 24,
  "auto_update": false,
  "notify_updates": true
}
```

**Usage:**
```python
# Get update report
from plugins.auto_update_plugin import AutoUpdatePlugin

plugin = AutoUpdatePlugin(event_bus)
plugin.activate()
print(plugin.get_update_report())
```

## Advanced Usage

### Scripting with the CLI

```bash
#!/bin/bash
# setup-dev-machine.sh

# Create snapshot before setup
./koala rollback create "Before dev setup"

# Install development tools
./koala install git python nodejs docker -y

# Check status
./koala status

# Sync to cloud
./koala sync push

echo "✅ Development environment setup complete!"
```

### Automation Example

```bash
# Daily update check script
#!/bin/bash

# Check for updates
./koala status | grep "Updates available"

if [ $? -eq 0 ]; then
    echo "Updates found! Creating backup..."
    ./koala rollback create "Before auto-update $(date)"

    # Install updates
    ./koala update --all -y

    # Sync to cloud
    ./koala sync push
fi
```

### Creating Custom Workflows

```bash
# Preset: AI Developer Setup
./koala install \
  python \
  jupyter \
  docker \
  vscode \
  ollama \
  lm-studio \
  -y

# Create snapshot after setup
./koala rollback create "AI Dev Environment Ready"

# Sync to other machines
./koala sync push
```

## Troubleshooting

### Plugin Not Loading

```bash
# Check plugin directory
ls -la ~/.koalas-forge/plugins/

# Verify plugin syntax
python3 -m py_compile ~/.koalas-forge/plugins/my_plugin.py

# Check plugin list
./koala plugin list
```

### Rollback Issues

```bash
# List all snapshots to verify ID
./koala rollback list

# Check system status
./koala status
```

### Cloud Sync Not Working

```bash
# Check sync status
./koala sync status

# Verify cloud storage is mounted
ls ~/Library/Mobile\ Documents/com~apple~CloudDocs/  # iCloud
ls ~/Dropbox/  # Dropbox
```

## Tips & Tricks

### Alias for Convenience

Add to your `.bashrc` or `.zshrc`:

```bash
# Quick alias
alias kf="./koala"

# Now you can use:
kf install git
kf status
kf rollback list
```

### Tab Completion (Future Feature)

Tab completion support coming in v1.3.0!

### Integration with Shell Scripts

```bash
# Save installation output
./koala install docker 2>&1 | tee install-log.txt

# Use in pipelines
./koala status | grep "Snapshots:" | awk '{print $2}'
```

## Next Steps

1. **Explore the Web GUI:** Run `./launch.sh` for the full web interface
2. **Create Custom Plugins:** See plugin examples in `plugins/`
3. **Automate Your Workflow:** Create shell scripts using the CLI
4. **Sync Across Machines:** Use cloud sync to replicate setups
5. **Contribute:** Share your plugins and workflows with the community

## Getting Help

- Full documentation: [README.md](README.md)
- Plugin development: Check `plugins/example_logger.py`
- Report issues: [GitHub Issues](https://github.com/mykolas-perevicius/koalas-forge/issues)

---

**Happy automating! 🐨**
