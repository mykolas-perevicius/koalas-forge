# Changelog

All notable changes to Koala's Forge will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-04

### 🎉 Initial Release - Complete Transformation from Ultimate System Setup

#### Added - Major Features

**Web Interface**
- 🎨 Beautiful modern web UI with pastel nature color scheme
- 🐨 Koala branding throughout the interface
- 📱 Fully responsive design for desktop, tablet, and mobile
- ✨ Smooth animations and transitions

**User Modes**
- 🧙 **Wizard Mode** - Guided setup for beginners
  - Select your needs (Development, AI, Creative, Gaming, etc.)
  - Get automatic recommendations
  - Review and customize before installing
- 🔧 **Expert Mode** - Full control for power users
  - Browse all 150+ applications
  - Custom configurations per app
  - Advanced filtering and search

**Installation Features**
- 🎯 **Smart Preset Packs**
  - AI Developer Pack (Ollama, LM Studio, Python, etc.)
  - Full Stack Developer (Git, Docker, Node, databases)
  - Creative Suite (Blender, GIMP, DaVinci Resolve)
  - Gaming Setup (Steam, Discord, OBS)
  - Security & Privacy (VPNs, password managers)
  - Data Science (Python, R, visualization tools)
- 🧪 **Dry Run Mode** - Test installations without making changes
- ⏸️ **Pause/Resume** - Take a break, continue later
- 🔄 **Update Apps** - Check and update installed applications
- 🗑️ **Uninstall Apps** - Remove applications through GUI
- 📊 **Real-time Progress** - Watch installations with detailed logs
- 🔍 **Detect Installed Apps** - See what's already on your system

**Backend**
- 🚀 Async Python server (aiohttp + websockets)
- 📡 WebSocket support for real-time updates
- 🌐 RESTful API endpoints
- 🛡️ Error handling and recovery
- 📝 Detailed logging system

**Application Management**
- 📦 150+ applications across 10+ categories
- 🎨 Custom install locations
- ⚙️ Per-app configuration options
- 💾 Export/import configurations
- 🔄 Overlapping preset selections

**User Experience**
- 🔍 **Search** - Find apps instantly
- 📑 **Categories** - Browse by type (Development, AI, Creative, etc.)
- ✅ **Status Badges** - See installed/update available
- 🌈 **Visual Feedback** - Clear success/error indicators
- ⌨️ **Keyboard Navigation** - Efficient workflows

**Developer Tools**
- 🎭 Playwright integration for automated testing
- 🎬 Demo recording scripts
- 🎨 GIF creation for documentation
- 📚 Comprehensive documentation

#### Technical Details

**Frontend**
- Pure HTML/CSS/JavaScript (no frameworks)
- Modern ES6+ JavaScript
- CSS Grid and Flexbox layouts
- Custom pastel color palette
- Accessibility considerations

**Backend**
- Python 3.9+ compatible
- Async/await architecture
- Multi-platform support (macOS, Linux, Windows-ready)
- Package manager integration (Homebrew, apt, etc.)

**Documentation**
- README.md - Complete overview
- QUICKSTART.md - Get started in 2 minutes
- CONTRIBUTING.md - Guide for contributors
- Demo materials and scripts

#### Application Categories

1. **AI & Machine Learning** (15+ apps)
   - Ollama, LM Studio, GPT4All, Jan
   - ComfyUI, Text Generation WebUI
   - CUDA toolkit support

2. **Development** (40+ apps)
   - Editors: VS Code, Cursor, Zed, Neovim
   - Languages: Python, Node.js, Rust, Go, Java
   - Tools: Git, Docker, Kubernetes, Postman

3. **Databases** (10+ apps)
   - PostgreSQL, MySQL, Redis, MongoDB
   - TablePlus, DBeaver

4. **Creative** (20+ apps)
   - 3D: Blender
   - 2D: GIMP, Inkscape, Krita
   - Video: DaVinci Resolve, OBS Studio
   - Audio: Audacity, Ardour

5. **Productivity** (25+ apps)
   - Note-taking: Obsidian, Notion
   - Communication: Slack, Discord, Zoom
   - Utilities: Rectangle, Raycast, Alfred

6. **Gaming & Entertainment** (15+ apps)
   - Platforms: Steam, Epic Games
   - Tools: Discord, OBS Studio
   - Media: Spotify, VLC

7. **Security** (10+ apps)
   - VPNs: NordVPN, ProtonVPN
   - Password Managers: 1Password, Bitwarden
   - Tools: Wireshark, Burp Suite

8. **Browsers** (5+ apps)
   - Chrome, Firefox, Brave, Arc

9. **Terminal Tools** (10+ apps)
   - iTerm2, Warp, tmux, htop, btop

10. **Cloud Tools** (10+ apps)
    - AWS CLI, Google Cloud SDK, Azure CLI
    - Terraform, kubectl, Helm

#### Launch Scripts

- `launch.sh` - One-command startup
- `create_demo_gif.sh` - Generate demo materials
- Simple, user-friendly interfaces

#### Comparison with Ninite

| Feature | Koala's Forge | Ninite |
|---------|---------------|--------|
| Price | Free & Open Source | Free/Paid |
| Apps | 150+ | ~90 |
| Interface | Modern Web UI | Windows installer |
| Platform | macOS, Linux, Windows | Windows only |
| AI Tools | Extensive | None |
| Pause/Resume | Yes | No |
| Uninstall | Yes | No |
| Dry Run | Yes | No |
| Custom Locations | Yes | Limited |
| Open Source | Yes | No |

### Changed
- Completely redesigned from "Ultimate System Setup" to "Koala's Forge"
- New branding, logo, and color scheme
- Modernized all user interactions

### Migration from Ultimate System Setup
- All existing functionality preserved
- New features added non-destructively
- Original configs still compatible

---

## Future Roadmap

### Planned for v1.1.0
- [ ] Windows native support (Chocolatey, winget)
- [ ] Linux package manager support (apt, dnf, pacman)
- [ ] App version tracking
- [ ] Installation history with rollback
- [ ] Dark mode toggle
- [ ] Multi-language support (i18n)

### Under Consideration
- [ ] Desktop app (Electron/Tauri)
- [ ] Cloud sync for configurations
- [ ] Community app submissions
- [ ] Auto-update checker
- [ ] Plugin system
- [ ] Scheduled installations

---

**Full Changelog**: https://github.com/mykolas-perevicius/koalas-forge/commits/main
