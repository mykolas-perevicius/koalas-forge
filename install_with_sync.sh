#!/usr/bin/env bash

# Enhanced installer with Terminal-GUI synchronization
# This wrapper adds progress tracking to the main installer

set -euo pipefail

# Source progress tracking
source "./scripts/progress_tracker.sh"
source "./scripts/websocket_client.sh" 2>/dev/null || true

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Show sync status
show_sync_status() {
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}🔄 Terminal-GUI Synchronization Status${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    # Check if GUI is running
    if check_gui_running 2>/dev/null; then
        echo -e "${GREEN}✅ Web GUI detected at http://localhost:8080${NC}"
        echo -e "${GREEN}   Progress will sync automatically!${NC}"
    else
        echo -e "${YELLOW}📊 Web GUI not detected${NC}"
        echo -e "${BLUE}   Start GUI with: ./launch_gui.sh${NC}"
        echo -e "${BLUE}   Progress file: /tmp/app_installer_progress.json${NC}"
    fi

    echo ""
}

# Enhanced install function with progress tracking
install_with_progress() {
    local mode="${1:-full}"
    shift

    # Show sync status
    show_sync_status

    # Initialize progress tracking
    init_progress "$mode"

    # Update progress: Starting
    update_progress 5 "Starting $mode installation"

    # Run actual installer with progress hooks
    (
        # Track output and update progress
        ./install.sh --$mode "$@" 2>&1 | while IFS= read -r line; do
            echo "$line"

            # Parse output for progress updates
            if [[ "$line" == *"Installing"* ]]; then
                # Extract package name if possible
                package=$(echo "$line" | grep -oE '[a-z0-9_-]+$' || echo "package")
                update_progress 20 "Installing $package"

            elif [[ "$line" == *"✅"* ]] && [[ "$line" == *"installed"* ]]; then
                # Package installed successfully
                package=$(echo "$line" | grep -oE '[a-z0-9_-]+' | head -1 || echo "package")
                track_package "$package" "success"

            elif [[ "$line" == *"❌"* ]] || [[ "$line" == *"Failed"* ]]; then
                # Package failed
                package=$(echo "$line" | grep -oE '[a-z0-9_-]+' | head -1 || echo "package")
                track_package "$package" "failed"

            elif [[ "$line" == *"Configuring"* ]]; then
                update_progress 70 "Configuring system"

            elif [[ "$line" == *"Optimizing"* ]]; then
                update_progress 85 "Optimizing performance"

            elif [[ "$line" == *"completed"* ]]; then
                update_progress 100 "Installation completed"
            fi

            # Send to WebSocket if available
            if check_gui_running 2>/dev/null; then
                if [[ "$line" == *"✅"* ]]; then
                    send_ws_message "$line" "success" 2>/dev/null || true
                elif [[ "$line" == *"❌"* ]] || [[ "$line" == *"Error"* ]]; then
                    send_ws_message "$line" "error" 2>/dev/null || true
                elif [[ "$line" == *"⚠"* ]] || [[ "$line" == *"Warning"* ]]; then
                    send_ws_message "$line" "warning" 2>/dev/null || true
                else
                    send_ws_message "$line" "info" 2>/dev/null || true
                fi
            fi
        done

        exit_code=$?

        # Complete progress tracking
        if [[ $exit_code -eq 0 ]]; then
            complete_progress "completed"
            echo -e "${GREEN}✅ Installation completed successfully${NC}"
        else
            complete_progress "failed"
            echo -e "${YELLOW}⚠️  Installation completed with errors${NC}"
        fi

        # Show final sync status
        echo ""
        echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        if check_gui_running 2>/dev/null; then
            echo -e "${GREEN}✅ Progress synced to Web GUI${NC}"
            echo -e "${BLUE}   View at: http://localhost:8080${NC}"
        else
            echo -e "${BLUE}📊 Progress saved to: /tmp/app_installer_progress.json${NC}"
        fi
        echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

        exit $exit_code
    )
}

# Main execution
main() {
    # Check for help
    if [[ "${1:-}" == "--help" ]] || [[ "${1:-}" == "-h" ]]; then
        echo "Enhanced Installer with Terminal-GUI Sync"
        echo ""
        echo "Usage: $0 [mode] [options]"
        echo ""
        echo "Modes:"
        echo "  full     - Install everything"
        echo "  ai       - AI/ML tools only"
        echo "  dev      - Development tools only"
        echo "  minimal  - Essential tools only"
        echo ""
        echo "Options:"
        echo "  --dry-run - Test mode without changes"
        echo ""
        echo "Examples:"
        echo "  $0 full              # Full installation with sync"
        echo "  $0 ai --dry-run      # Test AI installation"
        echo ""
        echo "Progress Sync:"
        echo "  - Automatically syncs with Web GUI if running"
        echo "  - Progress saved to: /tmp/app_installer_progress.json"
        echo "  - Start GUI with: ./launch_gui.sh"
        exit 0
    fi

    # Get mode (default to full)
    mode="${1:-full}"
    shift || true

    # Run installation with progress tracking
    install_with_progress "$mode" "$@"
}

# Run main function
main "$@"