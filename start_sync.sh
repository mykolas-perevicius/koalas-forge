#!/usr/bin/env bash

# 🔄 Quick Start Script for Terminal-GUI Sync
# Starts the GUI server cleanly and opens the browser

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
cat << "BANNER"
╔═══════════════════════════════════════════════════════════════╗
║        🔄 TERMINAL-GUI SYNC - QUICK START                     ║
╚═══════════════════════════════════════════════════════════════╝
BANNER
echo -e "${NC}"

# Step 1: Kill existing processes
echo -e "${YELLOW}Step 1: Cleaning up existing processes...${NC}"
killall python3 2>/dev/null || true
lsof -ti:8080,8765 | xargs kill -9 2>/dev/null || true
rm -f /tmp/app_installer_progress.json
echo -e "${GREEN}✅ Cleanup complete${NC}"
echo ""

# Step 2: Start GUI server
echo -e "${YELLOW}Step 2: Starting GUI server...${NC}"
python3 gui/gui_server.py > /tmp/gui_server.log 2>&1 &
sleep 3
echo -e "${GREEN}✅ GUI server started${NC}"
echo ""

# Step 3: Verify server is running
echo -e "${YELLOW}Step 3: Verifying server...${NC}"
if curl -s http://localhost:8080 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Server is responding${NC}"
else
    echo -e "${RED}❌ Server failed to start${NC}"
    echo "Check logs: tail -f /tmp/gui_server.log"
    exit 1
fi

# Step 4: Test API endpoint
echo -e "${YELLOW}Step 4: Testing sync API...${NC}"
if curl -s http://localhost:8080/api/terminal-progress > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Sync API is ready${NC}"
else
    echo -e "${RED}❌ Sync API not responding${NC}"
    exit 1
fi
echo ""

# Step 5: Open browser
echo -e "${YELLOW}Step 5: Opening browser...${NC}"
if command -v open &>/dev/null; then
    # macOS
    open http://localhost:8080
elif command -v xdg-open &>/dev/null; then
    # Linux
    xdg-open http://localhost:8080
elif command -v start &>/dev/null; then
    # Windows
    start http://localhost:8080
fi
echo -e "${GREEN}✅ Browser opened${NC}"
echo ""

# Show instructions
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ GUI is Ready!${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}Web Interface:${NC} http://localhost:8080"
echo -e "${BLUE}API Endpoint:${NC}  http://localhost:8080/api/terminal-progress"
echo -e "${BLUE}Progress File:${NC}  /tmp/app_installer_progress.json"
echo ""
echo -e "${YELLOW}Now run in another terminal:${NC}"
echo -e "  ${GREEN}./install.sh --minimal --dry-run${NC}"
echo -e "  ${GREEN}./install.sh --full${NC}"
echo -e "  ${GREEN}./install.sh --ai${NC}"
echo ""
echo -e "${CYAN}Watch the web interface update automatically!${NC}"
echo ""
echo -e "${BLUE}To stop the server:${NC}"
echo -e "  ${YELLOW}killall python3${NC}"
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"