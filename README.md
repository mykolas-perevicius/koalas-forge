# 🐨 Koala's Forge

**The free, powerful alternative to Ninite for 2025**

Choose your apps. Click install. Get on with your life.

![Version](https://img.shields.io/badge/version-1.1.1-success)
![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Windows-blue)
![License](https://img.shields.io/badge/license-MIT-green)

<!-- Demo GIF will be added here -->
<!-- ![Koala's Forge Demo](demo/koalas-forge-demo.gif) -->

---

## 🚀 What is Koala's Forge?

Koala's Forge is a modern, web-based application installer that lets you set up your entire system in minutes. Like Ninite, but **free**, **open-source**, and designed for everything you need in 2025 - from development tools to AI models to creative software.

### ✨ Why Koala's Forge?

- 🎨 **Beautiful Web Interface** - Modern, intuitive design with pastel nature colors
- 🎯 **Smart Presets** - One-click packs for AI Development, Creative Work, Gaming, and more
- 🔧 **Full Control** - Choose exactly what you want, configure install locations
- ⏸️ **Pause & Resume** - Installation taking too long? Pause and come back later
- 🔄 **Update & Uninstall** - Manage your apps long after installation
- 🧙 **Wizard Mode** - Perfect for beginners who just want it to work
- 📦 **150+ Applications** - Everything from VS Code to Blender to local AI models

## ⚡ Quick Start

### Launch Koala's Forge

```bash
# Clone the repository
git clone https://github.com/mykolas-perevicius/koalas-forge.git
cd koalas-forge

# Launch the web interface
./launch.sh
```

Then open your browser to **http://localhost:8080** and start selecting apps!

### Preset Packs (One-Click Install)

- **🤖 AI Developer Pack** - Local LLMs, Python, Jupyter, CUDA toolkit
- **💻 Full Stack Developer** - All languages, databases, Docker, cloud tools
- **🎨 Creative Suite** - Blender, GIMP, DaVinci Resolve, Audacity
- **🎮 Gaming Setup** - Steam, Discord, OBS Studio
- **🔒 Security & Privacy** - VPN, password managers, security tools
- **📊 Data Science** - Python, R, Jupyter, visualization tools

## 🎨 Features

### Modern Web Interface
- Beautiful pastel design inspired by nature 🌿
- Responsive layout works on any screen size
- Real-time installation progress with timer ⏱️
- Search and filter apps instantly
- Dark mode toggle 🌙

### 🆕 Smart Recommendations (v1.1.0)
- **AI-like suggestions** - Get intelligent app recommendations based on your selection
- **40+ relationships** - Complementary apps, dependencies, and workflow patterns
- **5 workflow patterns** - Web dev, AI dev, creative, gaming, data science
- **Top 6 display** - Most relevant recommendations with contextual reasoning
- **One-click add** - Instantly add recommended apps to your selection

### 📁 Installation Profiles (v1.1.0)
- **Save profiles** - Store your app selections with custom names and descriptions
- **One-click loading** - Instantly apply saved profiles
- **Share with teams** - Export profiles as JSON files
- **Import profiles** - Load shared configurations from files
- **Multi-machine setup** - Replicate setups across devices in seconds

### 💡 Quick Win Features (v1.1.0)
- **Installation Timer** - See elapsed time, remaining time, and speed (apps/min)
- **Disk Space Calculator** - Know exactly how much space you need with color-coded warnings
- **Recent Apps** - Discover new additions with animated "New!" badges

### Smart Installation
- **Dry run mode** - Test installations without making changes 🧪
- **Parallel downloads** - Install multiple apps simultaneously
- **Resume support** - Power went out? Pick up where you left off
- **Dependency handling** - Automatically installs requirements
- **Custom locations** - Choose where each app gets installed
- **Unattended mode** - Perfect for automation

### Application Management
- ✅ Install new applications
- 🔄 Update existing applications
- 🗑️ Uninstall applications
- 📊 View installed apps and versions
- 🔍 Detect what's already installed

## 📦 Application Categories

**Development** (40+ apps)
- Editors: VS Code, Cursor, Zed, Neovim
- Languages: Python, Node, Rust, Go, Java
- Tools: Git, Docker, Kubernetes, Postman
- Databases: PostgreSQL, MySQL, Redis, MongoDB

**AI & Machine Learning** (15+ apps)
- Ollama, LM Studio, GPT4All, Jan
- ComfyUI, Text Generation WebUI
- CUDA Toolkit, TensorFlow, PyTorch

**Creative** (20+ apps)
- 3D: Blender
- 2D: GIMP, Inkscape, Krita
- Video: DaVinci Resolve, OBS Studio
- Audio: Audacity, Ardour

**Productivity** (25+ apps)
- Note-taking: Obsidian, Notion
- Communication: Slack, Discord, Zoom
- Utilities: Rectangle, Raycast, Alfred

**Gaming & Entertainment** (15+ apps)
- Platforms: Steam, Epic Games
- Tools: Discord, OBS Studio
- Media: Spotify, VLC

**Security** (10+ apps)
- VPNs: NordVPN, ProtonVPN
- Password Managers: 1Password, Bitwarden
- Tools: Wireshark, Burp Suite

## 🖥️ System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **OS** | macOS 11+, Ubuntu 20.04+, Windows 10+ | Latest stable release |
| **RAM** | 4GB | 16GB+ (for AI workloads) |
| **Storage** | 20GB free | 100GB+ free |
| **Internet** | Required for downloads | Broadband connection |
| **GPU** | Optional | Recommended for AI/gaming |

## 🧙 Usage Modes

### Wizard Mode (Recommended for Beginners)
1. Launch Koala's Forge
2. Answer a few quick questions about what you need
3. Review the suggested apps
4. Click "Install" and relax ☕

### Expert Mode
1. Browse all 150+ applications
2. Select exactly what you want
3. Configure install locations and options
4. Install, update, or uninstall with full control

## 🎯 Example Workflows

### "I'm a new developer"
→ Use Wizard Mode → Select "Full Stack Developer" → Add GitHub Desktop → Install

### "I want to run AI models locally"
→ Expert Mode → AI Category → Select Ollama, LM Studio, ComfyUI → Install

### "Set up my new gaming PC"
→ Select "Gaming Setup" preset → Add your favorite launchers → Install

## 🛠️ Advanced Usage

```bash
# Launch with specific port
./launch.sh --port 3000

# CLI mode (no GUI)
./install.sh --apps "git,python,docker" --yes

# Update all installed apps
./install.sh --update-all

# Uninstall apps
./install.sh --uninstall "app1,app2"

# Export your configuration
./install.sh --export my-setup.json

# Install from saved configuration
./install.sh --import my-setup.json
```

## 🌟 Comparison with Ninite

| Feature | Koala's Forge 🐨 | Ninite |
|---------|-----------------|--------|
| **Price** | Free & Open Source | Free (basic) / Paid (Pro) |
| **App Selection** | 150+ apps | ~90 apps |
| **Interface** | Modern web UI | Windows installer only |
| **Platform** | macOS, Linux, Windows | Windows only |
| **AI/ML Tools** | ✅ Extensive | ❌ None |
| **Customization** | Full control | Limited |
| **Update Apps** | ✅ Yes | ✅ Yes (Pro only) |
| **Uninstall** | ✅ Yes | ❌ No |
| **Pause/Resume** | ✅ Yes | ❌ No |

## 📄 License

MIT License - Use it however you want!

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 💬 Support

- 🐛 [Report a bug](https://github.com/mykolas-perevicius/koalas-forge/issues)
- 💡 [Request a feature](https://github.com/mykolas-perevicius/koalas-forge/issues)
- 📖 [Read the docs](https://github.com/mykolas-perevicius/koalas-forge/wiki)

---

**Made with 💚 for developers, creators, and power users**

*Because setting up your computer shouldn't take all day* 🐨
