# 🐨 Koala's Forge - Quick Start Guide

Welcome to Koala's Forge! This guide will get you up and running in under 2 minutes.

## 🚀 Launch Koala's Forge

### Method 1: Web Interface (Recommended)

```bash
cd /Users/myko/app-installer
./launch.sh
```

The web interface will automatically open in your browser at **http://localhost:8080**

### Method 2: Lite GUI (Backup)

If you prefer a simple desktop interface:

```bash
cd /Users/myko/app-installer
python3 gui/koalas_forge_lite.py
```

## 🧙 First Time Setup

### Wizard Mode (Recommended for Beginners)

1. Launch Koala's Forge
2. Click "🧙 Wizard Mode" (should be selected by default)
3. Select what you want to do:
   - 💻 Development
   - 🤖 AI & ML
   - 🎨 Creative Work
   - 🎮 Gaming
   - 📊 Productivity
   - 🔒 Security
4. Click "Next →"
5. Review recommended apps
6. Click "Install Selected Apps"
7. Sit back and relax! ☕

### Expert Mode (For Power Users)

1. Click "🔧 Expert Mode"
2. Browse preset packs or search for specific apps
3. Select apps individually with checkboxes
4. Configure per-app settings (optional)
5. Click "Install Selected Apps"

## 🎯 Quick Presets

### AI Developer Pack
Perfect for ML engineers and AI researchers:
- Ollama (local LLMs)
- LM Studio
- Python 3.11
- Jupyter
- VS Code
- Cursor
- Docker

**Quick install:** Select "🤖 AI Developer" preset in Expert Mode

### Full Stack Developer
Everything you need for web development:
- Git
- Node.js
- Python
- Docker
- PostgreSQL
- Redis
- VS Code

**Quick install:** Select "💻 Full Stack Developer" preset in Expert Mode

### Creative Suite
For designers and content creators:
- Blender
- GIMP
- Inkscape
- DaVinci Resolve
- OBS Studio
- Audacity

**Quick install:** Select "🎨 Creative Suite" preset in Expert Mode

## 🔧 Advanced Features

### Pause & Resume Installation

Click the "Pause" button during installation to pause at any time. Your progress is saved!

### Custom Install Locations

Click "⚙️ Settings" on any app card to:
- Choose custom installation directory
- Configure app-specific options
- View dependencies

### Update Installed Apps

1. Go to Expert Mode
2. Apps with updates available show an "Update Available" badge
3. Select apps to update
4. Click "Update Selected Apps"

### Uninstall Apps

1. Select the apps you want to remove
2. Click the action menu (⋮)
3. Choose "Uninstall Selected Apps"

### Export Your Configuration

Save your app selections for later:

1. Select your apps
2. Click "Export Config"
3. Save the `.json` file

Load it on another machine:

```bash
./install.sh --import my-config.json
```

## 🌐 Using the Web Interface

### Navigation

- **Search Bar** - Find apps quickly by name
- **Category Tabs** - Filter by Development, AI, Creative, etc.
- **Preset Packs** - One-click installation bundles
- **Selection Counter** - Shows how many apps you've selected
- **Action Bar** - Install, clear, export controls (bottom of page)

### Installation Progress

During installation, you'll see:
- Real-time progress bar
- Current app being installed
- Detailed installation log
- Success/error messages
- Pause/Resume controls

## 💡 Tips & Tricks

1. **Multiple Presets**: You can select multiple preset packs! They'll combine intelligently.

2. **Search**: Use the search bar to quickly find specific apps like "docker" or "python"

3. **Platform Badges**: Each app shows which platforms it supports (mac, linux, windows)

4. **Already Installed**: Apps you already have show an "Installed" badge

5. **Background Installation**: Minimize the browser - installation continues!

6. **Resume After Restart**: If your computer restarts, relaunch and your queue is saved

## 🆘 Troubleshooting

### Port Already in Use

If port 8080 is busy, launch with a custom port:

```bash
./launch.sh --port 3000
```

### Installation Fails

1. Check the installation log for error details
2. Try installing the app individually
3. Check your internet connection
4. Ensure you have sufficient disk space

### Web Interface Won't Load

1. Ensure Python 3 is installed: `python3 --version`
2. Check if the server is running: `ps aux | grep koalas_forge`
3. Try the Lite GUI instead: `python3 gui/koalas_forge_lite.py`

### Permission Errors

Some apps may need administrator privileges:

```bash
sudo ./launch.sh
```

## 📚 Learn More

- **Full README**: See `README.md` for detailed feature list
- **Configuration**: Check `apps.yaml` to see all available apps
- **Logs**: Installation logs are in `logs/` directory
- **GitHub**: Report issues or contribute!

## 🎉 You're All Set!

Enjoy Koala's Forge! Setting up your computer has never been easier. 🐨

---

**Made with 💚 for developers, creators, and power users**

*Because setting up your computer shouldn't take all day*
