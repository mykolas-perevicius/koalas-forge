#!/usr/bin/env bash
# Ultimate System Setup - AI Lab + Complete Dev Environment

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

source "./scripts/utils.sh"

# Source progress tracking for terminal-GUI sync
if [[ -f "./scripts/progress_tracker.sh" ]]; then
    source "./scripts/progress_tracker.sh"
fi
if [[ -f "./scripts/websocket_client.sh" ]]; then
    source "./scripts/websocket_client.sh" 2>/dev/null || true
fi

# Disable sync flag (can be set to true with --no-sync)
DISABLE_SYNC=false

# Epic Banner
echo -e "${CYAN}"
cat << "BANNER"
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║           🚀 ULTIMATE SYSTEM SETUP INSTALLER 🚀              ║
║                                                               ║
║     Complete Dev Environment + AI Lab + Gaming Station       ║
║          Hardware Drivers + Security + Performance           ║
║                                                               ║
║                    100+ Tools & Applications                 ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
BANNER
echo -e "${NC}\n"

show_help() {
    cat << HELP
Usage: ./install.sh [OPTIONS]

QUICK OPTIONS:
  --full              Install everything (recommended)
  --ai                AI/LLM tools only
  --dev               Development environment only
  --minimal           Essential tools only

OPERATIONS:
  --detect-hardware   Scan hardware
  --drivers           Install drivers
  --optimize          Optimize system
  --dry-run           Test mode - simulate installation without changes
  --no-sync           Disable GUI synchronization
  --help              Show this help

Examples:
  ./install.sh --full           # Everything
  ./install.sh --ai --optimize  # AI lab setup
  ./install.sh --dev            # Dev tools only
  ./install.sh --full --dry-run # Test installation without changes

After installation:
  ollama run llama3.2           # Chat with AI
HELP
}

# Parse arguments
MODE=""
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --full)
            MODE="full"
            shift
            ;;
        --ai)
            MODE="ai"
            shift
            ;;
        --dev)
            MODE="dev"
            shift
            ;;
        --minimal)
            MODE="minimal"
            shift
            ;;
        --detect-hardware)
            MODE="detect"
            shift
            ;;
        --drivers)
            MODE="drivers"
            shift
            ;;
        --optimize)
            MODE="optimize"
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --no-sync)
            DISABLE_SYNC=true
            shift
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Default to full
if [[ -z "$MODE" ]]; then
    MODE="full"
fi

# Initialize progress tracking if not disabled
if [[ "$DISABLE_SYNC" != "true" ]] && [[ -f "./scripts/progress_tracker.sh" ]]; then
    # Check if GUI is running
    if check_gui_running 2>/dev/null; then
        log_success "✅ Web GUI detected - progress will sync automatically!"
        log_info "   View at: http://localhost:8080"
    else
        log_info "📊 Progress tracking enabled"
        log_info "   Start GUI with: ./launch_gui.sh"
        log_info "   Progress file: /tmp/app_installer_progress.json"
    fi

    # Initialize progress tracking
    init_progress "$MODE"
    update_progress 5 "Starting $MODE installation"
fi

# Check if dry run mode
if [[ "$DRY_RUN" == "true" ]]; then
    log_info "🧪 DRY RUN MODE - No actual changes will be made"

    # Update progress for dry run
    if [[ "$DISABLE_SYNC" != "true" ]] && [[ -f "./scripts/progress_tracker.sh" ]]; then
        update_progress 10 "Running in dry run mode"
    fi

    source "./scripts/dry_run_test.sh"
    run_dry_run "$MODE"

    # Complete progress for dry run
    if [[ "$DISABLE_SYNC" != "true" ]] && [[ -f "./scripts/progress_tracker.sh" ]]; then
        update_progress 100 "Dry run completed"
        complete_progress "completed"
    fi

    exit 0
fi

# Pre-flight checks (skip for detect)
if [[ "$MODE" != "detect" ]]; then
    preflight_checks || {
        log_error "Pre-flight checks failed"
        exit 1
    }
fi

# Execute based on mode
case "$MODE" in
    full)
        log_info "FULL INSTALLATION - Installing everything..."
        source "./scripts/install_apps.sh"
        install_all
        source "./scripts/setup_ai.sh"
        main
        source "./scripts/install_drivers.sh"
        main
        source "./scripts/optimize_system.sh"
        main
        ;;
        
    ai)
        log_info "AI/LLM Installation..."
        source "./scripts/install_apps.sh"
        install_category "ai_local"
        source "./scripts/setup_ai.sh"
        main
        ;;
        
    dev)
        log_info "Development Environment..."
        source "./scripts/install_apps.sh"
        install_category "development_core"
        install_category "development_tools"
        install_category "databases"
        ;;
        
    minimal)
        log_info "Minimal Installation..."
        source "./scripts/install_apps.sh"
        install_category "development_core"
        ;;
        
    detect)
        source "./scripts/detect_hardware.sh"
        main
        ;;
        
    drivers)
        source "./scripts/install_drivers.sh"
        main
        ;;
        
    optimize)
        source "./scripts/optimize_system.sh"
        main
        ;;
esac

# Final message
log_section "Installation Complete!"

if [[ "$MODE" == "full" ]] || [[ "$MODE" == "ai" ]]; then
    echo ""
    log_info "🤖 AI Quick Start:"
    echo "  Chat with AI: ollama run llama3.2"
    echo "  List models: ollama list"
    echo ""
fi

log_success "System ready! Run './install.sh --help' for more options"
