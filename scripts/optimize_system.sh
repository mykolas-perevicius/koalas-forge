#!/usr/bin/env bash
# System optimization

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/utils.sh"

optimize_mac() {
    log_section "macOS Optimization"
    
    # Disable animations for speed
    defaults write NSGlobalDomain NSAutomaticWindowAnimationsEnabled -bool false
    defaults write com.apple.dock expose-animation-duration -float 0.1
    
    # Increase file limits
    sudo launchctl limit maxfiles 65536 200000
    
    log_success "macOS optimized"
}

optimize_linux() {
    log_section "Linux Optimization"
    
    # Increase file descriptors
    echo "* soft nofile 65536" | sudo tee -a /etc/security/limits.conf
    
    # Performance governor
    if command_exists cpupower; then
        sudo cpupower frequency-set -g performance 2>/dev/null || true
    fi
    
    # NVIDIA settings
    if command_exists nvidia-smi; then
        sudo nvidia-smi -pm 1 2>/dev/null || true
    fi
    
    log_success "Linux optimized"
}

main() {
    log_section "System Optimization"
    
    local platform=$(detect_platform)
    
    case "$platform" in
        mac) optimize_mac ;;
        linux) optimize_linux ;;
        windows) log_info "Run Windows in High Performance mode" ;;
    esac
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main
fi
