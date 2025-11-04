# 🐨 Koala's Forge - Frequently Asked Questions

## General Questions

### What is Koala's Forge?
Koala's Forge is a free, open-source application installer that helps you set up your entire system in minutes. Think of it as a modern alternative to Ninite, but with more apps, better UI, and support for macOS, Linux, and Windows.

### Is it really free?
Yes! Koala's Forge is completely free and open-source under the MIT license. No hidden costs, no premium tiers.

### What platforms are supported?
- **macOS** 11+ (Full support)
- **Linux** (Ubuntu 20.04+, planned)
- **Windows** 10+ (planned)

### How many applications are available?
Currently 150+ applications across 10+ categories including Development, AI/ML, Creative, Gaming, Security, and more.

## Installation Questions

### Do I need administrator privileges?
Some applications require administrator privileges to install. Koala's Forge will prompt you when needed.

### Can I pause and resume installations?
Yes! Click the "Pause" button during installation. Your progress is saved and you can resume anytime.

### What is Dry Run mode?
Dry Run mode simulates the installation without actually installing anything. It's perfect for:
- Testing before committing
- Checking disk space requirements
- Verifying app compatibility
- Previewing what will be installed

### Can I install apps to custom locations?
Yes! Click the "⚙️ Settings" button on any app card to choose a custom installation directory.

### What if an installation fails?
- Check the installation log for detailed error messages
- Ensure you have sufficient disk space
- Check your internet connection
- Try installing the app individually
- Report persistent issues on GitHub

### Can I install multiple apps at once?
Yes! Select as many apps as you want. Koala's Forge will queue them and install efficiently.

### How long does installation take?
It depends on:
- Number of apps selected
- Your internet speed
- System specifications
- App sizes

Typically:
- Small apps (< 100MB): 1-2 minutes
- Medium apps (100MB - 1GB): 5-10 minutes
- Large apps (> 1GB): 15-30 minutes

## Feature Questions

### What's the difference between Wizard and Expert mode?
- **Wizard Mode**: Answer a few questions, get automatic recommendations. Perfect for beginners.
- **Expert Mode**: Browse all apps, customize everything. Perfect for power users who know exactly what they want.

### Can I use both modes?
Absolutely! Switch between them anytime. You can start in Wizard mode and switch to Expert for fine-tuning.

### What are preset packs?
Preset packs are curated bundles of related applications:
- AI Developer Pack: Ollama, Python, Jupyter, etc.
- Full Stack Developer: Git, Docker, databases, etc.
- Creative Suite: Blender, GIMP, video editors, etc.

You can select multiple packs and they'll combine intelligently.

### Can I save my selection for later?
Yes! Click "Export Config" to save your app selection as a JSON file. Import it later or share with others.

### How do I update installed apps?
Apps with available updates show an "Update Available" badge. Select them and click "Update Selected Apps".

### Can I uninstall apps through Koala's Forge?
Yes! Select installed apps and choose "Uninstall" from the action menu.

## Technical Questions

### How does Koala's Forge work?
Koala's Forge uses package managers (like Homebrew on macOS) to install applications. It's a beautiful interface on top of tried-and-true package management tools.

### Does it require internet?
Yes, for downloading applications. The web interface runs locally and doesn't send data anywhere.

### Is my data collected?
No. Koala's Forge:
- Runs entirely on your local machine
- Doesn't collect analytics
- Doesn't send data to external servers
- Is fully open-source (you can verify this)

### Can I use it offline?
You need internet to download apps, but you can:
- Browse the interface offline
- Export configurations offline
- Use the Lite GUI without a browser

### What package managers are supported?
- **macOS**: Homebrew (primary)
- **Linux**: apt, dnf, pacman (planned)
- **Windows**: Chocolatey, winget (planned)

### Can I add custom applications?
Yes! Edit `apps.yaml` to add your own applications. See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## Troubleshooting

### The web interface won't load
1. Check if Python 3 is installed: `python3 --version`
2. Install dependencies: `pip3 install aiohttp websockets pyyaml`
3. Try the Lite GUI: `python3 gui/koalas_forge_lite.py`
4. Run verification: `./verify_installation.sh`

### Port 8080 is already in use
Launch with a custom port:
```bash
./launch.sh --port 3000
```

### Installation is stuck
1. Check the installation log for errors
2. Try pausing and resuming
3. Cancel and retry the specific app
4. Check your internet connection

### Homebrew is not installed (macOS)
Koala's Forge can help install Homebrew. You'll be prompted on first run.

### I get permission errors
Some apps need administrator access:
```bash
sudo ./launch.sh
```

### The theme toggle isn't working
Clear your browser cache or try:
- Press Ctrl+Shift+R (hard refresh)
- Open in incognito/private mode
- Check localStorage is enabled

## Comparison Questions

### How is this different from Ninite?
See the comparison table in [README.md](README.md). Key differences:
- Koala's Forge is free and open-source
- 150+ apps vs Ninite's ~90
- Works on macOS, Linux, Windows (vs Windows only)
- Modern web interface
- More features (pause/resume, dry run, uninstall, etc.)

### Why not just use Homebrew directly?
You absolutely can! Koala's Forge is for people who want:
- A visual interface
- Smart recommendations
- Preset packs for common setups
- Easy discovery of new apps
- One-click installation of multiple apps

### Can it replace [other tool]?
Koala's Forge is designed to complement, not replace, your existing tools. Use it alongside your package manager, IDE, or other automation tools.

## Security Questions

### Is it safe to use?
Yes! Koala's Forge:
- Is open-source (verify the code yourself)
- Uses trusted package managers
- Doesn't execute arbitrary code
- Shows exactly what it will do (especially in Dry Run mode)

### How do I know apps are legitimate?
Koala's Forge only installs from official package manager repositories (like Homebrew), which vet applications.

### Can I review what will be installed?
Yes! Use Dry Run mode to see exactly what will happen without making changes.

### What permissions does it need?
- Internet access (to download apps)
- File system access (to install apps)
- Administrator access (only for certain apps)

## Contributing Questions

### Can I add my favorite app?
Yes! Open an "App Request" issue on GitHub or submit a pull request. See [CONTRIBUTING.md](CONTRIBUTING.md).

### How can I contribute?
Many ways:
- Add new applications
- Improve documentation
- Report bugs
- Suggest features
- Help other users
- Share Koala's Forge with others

### I found a bug, what do I do?
Open a bug report on GitHub with:
- Steps to reproduce
- Expected vs actual behavior
- Your system info
- Installation logs (if applicable)

## Getting Help

### Where can I get support?
- 📖 Read the [QUICKSTART.md](QUICKSTART.md) guide
- 🐛 Open an issue on [GitHub](https://github.com/mykolas-perevicius/koalas-forge/issues)
- 💬 Check existing issues for solutions
- ⌨️ See [KEYBOARD_SHORTCUTS.md](KEYBOARD_SHORTCUTS.md) for tips

### Is there a community?
We're building one! Join the discussion on GitHub.

### How often is Koala's Forge updated?
Check the [CHANGELOG.md](CHANGELOG.md) for version history. New apps and features are added regularly.

---

**Still have questions?** [Open an issue](https://github.com/mykolas-perevicius/koalas-forge/issues) and we'll help you out! 🐨
