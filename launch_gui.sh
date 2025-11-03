#!/usr/bin/env bash

# 🚀 GUI Launcher for Speedy App Installer
# Launches either the web interface or tkinter GUI

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GUI_DIR="$SCRIPT_DIR/gui"

# Default GUI type
GUI_TYPE="${1:-web}"

# Function to check Python dependencies
check_python_deps() {
    local missing_deps=()

    # Check for Python 3
    if ! command -v python3 &>/dev/null; then
        echo -e "${RED}❌ Python 3 is not installed${NC}"
        echo "Please install Python 3 first"
        exit 1
    fi

    # Check for required packages based on GUI type
    if [[ "$GUI_TYPE" == "web" ]]; then
        python3 -c "import aiohttp" 2>/dev/null || missing_deps+=("aiohttp")
        python3 -c "import websockets" 2>/dev/null || missing_deps+=("websockets")
    elif [[ "$GUI_TYPE" == "tkinter" ]]; then
        python3 -c "import tkinter" 2>/dev/null || missing_deps+=("tkinter")
        python3 -c "import yaml" 2>/dev/null || missing_deps+=("pyyaml")
    fi

    # Install missing dependencies
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        echo -e "${YELLOW}Installing required Python packages: ${missing_deps[*]}${NC}"
        pip3 install ${missing_deps[@]} || {
            echo -e "${RED}Failed to install dependencies${NC}"
            exit 1
        }
    fi
}

# Function to launch web GUI
launch_web_gui() {
    echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║           🌐 LAUNCHING WEB INTERFACE                          ║${NC}"
    echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    # Check dependencies
    check_python_deps

    # Start the server
    echo -e "${GREEN}Starting web server...${NC}"
    echo -e "${BLUE}  Web Interface: http://localhost:8080${NC}"
    echo -e "${BLUE}  WebSocket API: ws://localhost:8765${NC}"
    echo ""
    echo -e "${YELLOW}Opening browser in 3 seconds...${NC}"

    # Start server in background
    cd "$GUI_DIR"
    python3 gui_server.py &
    SERVER_PID=$!

    # Wait for server to start
    sleep 3

    # Open browser
    if command -v open &>/dev/null; then
        # macOS
        open http://localhost:8080
    elif command -v xdg-open &>/dev/null; then
        # Linux
        xdg-open http://localhost:8080
    elif command -v start &>/dev/null; then
        # Windows
        start http://localhost:8080
    else
        echo -e "${YELLOW}Please open your browser and navigate to: http://localhost:8080${NC}"
    fi

    echo ""
    echo -e "${GREEN}✅ Web interface is running${NC}"
    echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"

    # Wait for server process
    wait $SERVER_PID
}

# Function to launch tkinter GUI
launch_tkinter_gui() {
    echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║           🖥️  LAUNCHING DESKTOP GUI                           ║${NC}"
    echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    # Check dependencies
    check_python_deps

    # Check if running in SSH or headless environment
    if [[ -z "${DISPLAY}" ]] && [[ ! "$OSTYPE" == "darwin"* ]]; then
        echo -e "${RED}❌ No display detected. Cannot run desktop GUI.${NC}"
        echo -e "${YELLOW}Try the web interface instead: $0 web${NC}"
        exit 1
    fi

    # Launch the GUI
    echo -e "${GREEN}Starting desktop GUI...${NC}"
    cd "$GUI_DIR"
    python3 installer_gui.py
}

# Function to show help
show_help() {
    cat << EOF
${CYAN}Speedy App Installer - GUI Launcher${NC}

Usage: $0 [option]

Options:
    web       Launch web-based interface (default)
    tkinter   Launch desktop GUI application
    desktop   Alias for tkinter
    help      Show this help message

Examples:
    $0              # Launch web interface
    $0 web          # Launch web interface
    $0 tkinter      # Launch desktop GUI
    $0 desktop      # Launch desktop GUI

Web Interface:
    - Modern, responsive design
    - Accessible from any browser
    - Real-time installation progress
    - WebSocket communication

Desktop GUI:
    - Native desktop application
    - Tkinter-based interface
    - Direct system integration
    - Requires display environment

EOF
}

# Main execution
main() {
    case "$GUI_TYPE" in
        web|server)
            launch_web_gui
            ;;
        tkinter|desktop|gui)
            launch_tkinter_gui
            ;;
        help|-h|--help)
            show_help
            ;;
        *)
            echo -e "${RED}Unknown option: $GUI_TYPE${NC}"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Trap Ctrl+C to cleanup
trap 'echo -e "\n${YELLOW}Shutting down GUI...${NC}"; kill $SERVER_PID 2>/dev/null || true; exit 0' INT TERM

# Run main function
main "$@"