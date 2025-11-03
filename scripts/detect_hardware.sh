#!/usr/bin/env bash
# Hardware detection

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/utils.sh"

REPORT="../detected_hardware.txt"

detect_mac_hardware() {
    log_section "macOS Hardware Detection"
    
    {
        echo "=== System ==="
        system_profiler SPHardwareDataType | grep -E "Model|Processor|Memory|Graphics"
        
        echo -e "\n=== GPU ==="
        system_profiler SPDisplaysDataType | grep -E "Chipset|VRAM"
        
        echo -e "\n=== USB Devices ==="
        system_profiler SPUSBDataType | grep -E "Product ID|Manufacturer" | head -20
        
        echo -e "\n=== Audio ==="
        system_profiler SPAudioDataType | grep "Device Name"
        
    } > "$REPORT"
    
    log_success "Hardware report: $REPORT"
}

detect_linux_hardware() {
    log_section "Linux Hardware Detection"
    
    {
        echo "=== CPU ==="
        lscpu | head -15
        
        echo -e "\n=== GPU ==="
        lspci | grep -i vga
        if command_exists nvidia-smi; then
            nvidia-smi
        fi
        
        echo -e "\n=== USB ==="
        lsusb | head -20
        
        echo -e "\n=== Memory ==="
        free -h
        
    } > "$REPORT"
    
    log_success "Hardware report: $REPORT"
}

detect_windows_hardware() {
    log_section "Windows Hardware Detection"
    
    {
        echo "=== System ==="
        wmic computersystem get model,manufacturer 2>/dev/null
        
        echo -e "\n=== GPU ==="
        wmic path win32_VideoController get name 2>/dev/null
        
        echo -e "\n=== CPU ==="
        wmic cpu get name 2>/dev/null
        
    } > "$REPORT"
    
    log_success "Hardware report: $REPORT"
}

main() {
    local platform=$(detect_platform)
    
    case "$platform" in
        mac) detect_mac_hardware ;;
        linux) detect_linux_hardware ;;
        windows) detect_windows_hardware ;;
        *) log_error "Unknown platform" ;;
    esac
    
    cat "$REPORT"
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main
fi
