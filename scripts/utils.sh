#!/usr/bin/env bash
# Utility functions for app-installer

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ${NC}  $1"
}

log_success() {
    echo -e "${GREEN}✅${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠️${NC}  $1"
}

log_error() {
    echo -e "${RED}❌${NC} $1"
}

log_section() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}📦 $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

# Platform detection
detect_platform() {
    case "$OSTYPE" in
        darwin*)  echo "mac" ;;
        linux*)   echo "linux" ;;
        msys*|cygwin*|mingw*) echo "windows" ;;
        *)        echo "unknown" ;;
    esac
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if Homebrew is installed
check_homebrew() {
    if ! command_exists brew; then
        log_error "Homebrew not found. Installing..."
        if [[ "$(detect_platform)" == "mac" ]] || [[ "$(detect_platform)" == "linux" ]]; then
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            
            # Add Homebrew to PATH for Linux
            if [[ "$(detect_platform)" == "linux" ]]; then
                echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"' >> ~/.bashrc
                eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
            fi
        else
            log_error "Homebrew installation required. Visit https://brew.sh"
            return 1
        fi
    fi
    log_success "Homebrew found"
    return 0
}

# Disk space check (GB)
check_disk_space() {
    local required_gb=10
    local available=0
    
    if [[ "$(detect_platform)" == "mac" ]]; then
        available=$(df -g . | awk 'NR==2 {print $4}')
    else
        available=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
    fi
    
    if [[ $available -lt $required_gb ]]; then
        log_error "Insufficient disk space. Need ${required_gb}GB, have ${available}GB"
        return 1
    fi
    log_success "Disk space OK (${available}GB available)"
    return 0
}

# Pre-flight checks
preflight_checks() {
    log_section "Pre-flight Checks"
    
    # Internet connectivity
    if ! ping -c 1 8.8.8.8 >/dev/null 2>&1; then
        log_error "No internet connection"
        return 1
    fi
    log_success "Internet connection OK"
    
    # Disk space
    check_disk_space || return 1
    
    # Homebrew
    check_homebrew || return 1
    
    # Sudo access (non-Windows)
    if [[ "$(detect_platform)" != "windows" ]]; then
        if ! sudo -n true 2>/dev/null; then
            log_warning "Sudo access required"
            sudo -v || {
                log_error "Sudo authentication failed"
                return 1
            }
        fi
        log_success "Admin privileges OK"
    fi
    
    return 0
}

# Failure tracking
declare -a FAILED_INSTALLS=()

add_failure() {
    FAILED_INSTALLS+=("$1")
}

report_failures() {
    if [[ ${#FAILED_INSTALLS[@]} -gt 0 ]]; then
        log_section "Installation Summary"
        log_warning "${#FAILED_INSTALLS[@]} installation(s) failed:"
        for app in "${FAILED_INSTALLS[@]}"; do
            echo "  ❌ $app"
        done
        echo ""
        log_info "Check logs in ./logs/ for details"
        return 1
    else
        log_section "Installation Summary"
        log_success "All installations completed successfully!"
        return 0
    fi
}

# Check GPU
check_gpu() {
    local platform=$(detect_platform)
    
    case "$platform" in
        mac)
            if sysctl -n machdep.cpu.brand_string | grep -q "Apple"; then
                echo "apple_silicon"
            else
                echo "intel_mac"
            fi
            ;;
        linux)
            if command_exists nvidia-smi; then
                echo "nvidia"
            elif lspci | grep -qi "amd.*vga"; then
                echo "amd"
            else
                echo "cpu_only"
            fi
            ;;
        windows)
            echo "check_manually"
            ;;
    esac
}
