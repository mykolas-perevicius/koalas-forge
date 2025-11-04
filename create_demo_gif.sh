#!/bin/bash
#
# 🐨 Koala's Forge - Create Demo GIF
# Creates a demo GIF from screenshots
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEMO_DIR="$SCRIPT_DIR/demo"

echo "🎬 Creating Koala's Forge Demo GIF..."

# Check for ImageMagick (for GIF creation)
if ! command -v convert &> /dev/null; then
    echo "📦 ImageMagick not found. Installing..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install imagemagick
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt-get install -y imagemagick
    fi
fi

# Check if demo directory exists and has screenshots
if [ ! -d "$DEMO_DIR" ] || [ -z "$(ls -A $DEMO_DIR/*.png 2>/dev/null)" ]; then
    echo "📸 No screenshots found. Running demo recording script..."
    cd "$SCRIPT_DIR"
    python3 tests/demo_recording.py
fi

echo "🖼️  Creating GIF from screenshots..."

# Resize images for GIF (to reduce file size)
cd "$DEMO_DIR"
mkdir -p resized

for img in *.png; do
    if [ -f "$img" ]; then
        convert "$img" -resize 1280x720 "resized/$img"
    fi
done

# Create GIF from resized images
convert -delay 150 -loop 0 resized/*.png koalas-forge-demo.gif

# Optimize GIF size
if command -v gifsicle &> /dev/null; then
    gifsicle -O3 --colors 256 koalas-forge-demo.gif -o koalas-forge-demo-optimized.gif
    mv koalas-forge-demo-optimized.gif koalas-forge-demo.gif
    echo "✅ GIF optimized with gifsicle"
fi

# Clean up
rm -rf resized

echo ""
echo "🎉 Demo GIF created successfully!"
echo "📁 Location: $DEMO_DIR/koalas-forge-demo.gif"
echo "📊 Size: $(du -h "$DEMO_DIR/koalas-forge-demo.gif" | cut -f1)"
echo ""
echo "You can now add this to your README!"
