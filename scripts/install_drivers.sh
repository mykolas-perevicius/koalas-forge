#!/usr/bin/env bash
# Install hardware drivers

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/utils.sh"

install_mac_drivers() {
    log_section "macOS Driver Installation"
    
    # Check for peripherals and install software
    if system_profiler SPUSBDataType | grep -qi "logitech"; then
        log_info "Logitech detected"
        brew install --cask logi-options-plus 2>/dev/null || true
    fi
    
    if system_profiler SPUSBDataType | grep -qi "razer"; then
        log_info "Razer detected"
        brew install --cask razer-synapse 2>/dev/null || true
    fi
    
    log_success "macOS drivers checked"
}

install_linux_drivers() {
    log_section "Linux Driver Installation"
    
    # NVIDIA
    if lspci | grep -qi nvidia; then
        log_info "NVIDIA GPU detected"
        if ! command_exists nvidia-smi; then
            if command_exists apt; then
                sudo ubuntu-drivers autoinstall
                log_success "NVIDIA driver installed (reboot required)"
            fi
        fi
    fi
    
    # Audio
    if command_exists apt; then
        sudo apt install -y alsa-utils pulseaudio 2>/dev/null || true
    fi
    
    log_success "Linux drivers checked"
}

install_windows_drivers() {
    log_section "Windows Driver Installation"
    
    log_info "Windows driver installation:"
    echo "  1. Run Windows Update"
    echo "  2. Download GPU drivers:"
    echo "     NVIDIA: https://www.nvidia.com/drivers"
    echo "     AMD: https://www.amd.com/support"
}

main() {
    log_section "Driver Installation"
    
    local platform=$(detect_platform)
    
    case "$platform" in
        mac) install_mac_drivers ;;
        linux) install_linux_drivers ;;
        windows) install_windows_drivers ;;
    esac
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main
fi
