# 🎬 Koala's Forge Demo

This directory contains demo materials for Koala's Forge.

## Creating Demo Materials

### Automated Demo Recording

Run the Playwright script to automatically record a demo:

```bash
cd /Users/myko/app-installer
python3 tests/demo_recording.py
```

This will:
- Start the server
- Open a browser
- Navigate through key features
- Take screenshots at each step
- Record a video

### Creating GIF

Convert the demo into a GIF:

```bash
./create_demo_gif.sh
```

This will create an optimized GIF suitable for README.

## Manual Screenshots

To take manual screenshots:

1. Launch Koala's Forge: `./launch.sh`
2. Open browser to `http://localhost:8080`
3. Navigate to features you want to showcase
4. Take screenshots

## What to Showcase

Key features to highlight in demos:

- ✨ Beautiful pastel UI with koala branding
- 🧙 Wizard Mode for beginners
- 🔧 Expert Mode with full control
- 🎯 Preset packs for quick setup
- 🔍 Search and category filtering
- 🧪 Dry run mode
- ⏸️ Pause/resume functionality
- 📊 Real-time installation progress

## Demo Files

- `koalas-forge-demo.gif` - Animated demo GIF
- `01-landing.png` - Landing page
- `02-wizard-mode.png` - Wizard interface
- `05-expert-mode.png` - Expert mode with presets
- `07-app-grid.png` - App selection grid
- `11-installation-modal.png` - Installation in progress
