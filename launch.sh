#!/bin/bash
#
# 🐨 Koala's Forge Launcher
# Simple script to launch the web interface
#

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${GREEN}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                    🐨 KOALA'S FORGE 🐨                       ║"
echo "║          Choose your apps. Click install. Done.               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}Python 3 not found. Installing...${NC}"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install python@3.11
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt-get update && sudo apt-get install -y python3 python3-pip
    fi
fi

# Install Python dependencies
echo -e "${BLUE}📦 Installing dependencies...${NC}"
python3 -m pip install --quiet --upgrade pip
python3 -m pip install --quiet aiohttp websockets pyyaml

# Parse arguments
PORT=8080
WS_PORT=8765

while [[ $# -gt 0 ]]; do
    case $1 in
        --port)
            PORT="$2"
            shift 2
            ;;
        --ws-port)
            WS_PORT="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: ./launch.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --port PORT        HTTP server port (default: 8080)"
            echo "  --ws-port PORT     WebSocket server port (default: 8765)"
            echo "  --help, -h         Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Launch the server
echo -e "${GREEN}🚀 Launching Koala's Forge...${NC}"
echo -e "${BLUE}   Web Interface: http://localhost:$PORT${NC}"
echo -e "${BLUE}   WebSocket API: ws://localhost:$WS_PORT${NC}"
echo ""
echo -e "${YELLOW}💡 Opening your browser...${NC}"

# Open browser (platform specific)
sleep 2
if [[ "$OSTYPE" == "darwin"* ]]; then
    open "http://localhost:$PORT" 2>/dev/null || true
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xdg-open "http://localhost:$PORT" 2>/dev/null || true
fi

# Start the server
python3 gui/koalas_forge_server.py
