#!/usr/bin/env bash

# 🛡️ Enhanced Error Handling System for Speedy App Installer
# Provides comprehensive error handling, logging, and recovery mechanisms

set -euo pipefail  # Exit on error, undefined variables, and pipe failures

# Error codes
readonly ERR_GENERAL=1
readonly ERR_DEPENDENCY=2
readonly ERR_NETWORK=3
readonly ERR_PERMISSION=4
readonly ERR_DISK_SPACE=5
readonly ERR_TIMEOUT=6
readonly ERR_INVALID_ARG=7
readonly ERR_FILE_NOT_FOUND=8
readonly ERR_COMMAND_FAILED=9
readonly ERR_USER_ABORT=10

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly MAGENTA='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m' # No Color

# Error log file
ERROR_LOG="${ERROR_LOG:-logs/error_$(date +%Y%m%d_%H%M%S).log}"
mkdir -p "$(dirname "$ERROR_LOG")"

# Stack trace array
declare -a ERROR_STACK=()

# Installation state for rollback
declare -a INSTALLED_PACKAGES=()
declare -a MODIFIED_FILES=()
declare -a CREATED_DIRS=()

# Backup directory
BACKUP_DIR="${BACKUP_DIR:-backups/$(date +%Y%m%d_%H%M%S)}"

# Initialize error handling
initialize_error_handler() {
    # Set up error traps
    trap 'error_handler $? $LINENO "$BASH_COMMAND" $(printf "%s " "${BASH_SOURCE[@]}")' ERR
    trap 'cleanup_handler' EXIT
    trap 'interrupt_handler' INT TERM

    # Create error log
    echo "=== Error Handler Initialized ===" >> "$ERROR_LOG"
    echo "Date: $(date)" >> "$ERROR_LOG"
    echo "Script: $0" >> "$ERROR_LOG"
    echo "PID: $$" >> "$ERROR_LOG"
    echo "=================================" >> "$ERROR_LOG"
}

# Main error handler
error_handler() {
    local exit_code=$1
    local line_number=$2
    local command=$3
    shift 3
    local script_trace=("$@")

    # Don't trigger on user abort
    if [[ $exit_code -eq $ERR_USER_ABORT ]]; then
        return
    fi

    # Log error details
    log_error "ERROR: Command failed with exit code $exit_code"
    log_error "Line: $line_number"
    log_error "Command: $command"
    log_error "Script trace: ${script_trace[*]}"

    # Categorize error
    local error_type=$(categorize_error "$exit_code" "$command")

    # Display user-friendly error message
    display_error "$error_type" "$command" "$line_number"

    # Attempt recovery
    if attempt_recovery "$error_type" "$command"; then
        log_info "Recovery successful, continuing..."
        return 0
    fi

    # Offer rollback option
    if [[ ${#INSTALLED_PACKAGES[@]} -gt 0 ]] || [[ ${#MODIFIED_FILES[@]} -gt 0 ]]; then
        if prompt_user "Do you want to rollback changes?"; then
            perform_rollback
        fi
    fi

    # Generate error report
    generate_error_report "$exit_code" "$line_number" "$command" "$error_type"

    # Exit with original error code
    exit "$exit_code"
}

# Categorize error based on exit code and command
categorize_error() {
    local exit_code=$1
    local command=$2

    # Check for common error patterns
    if [[ $command == *"brew"* ]] || [[ $command == *"apt"* ]] || [[ $command == *"yum"* ]]; then
        echo "package_manager"
    elif [[ $command == *"curl"* ]] || [[ $command == *"wget"* ]] || [[ $command == *"git clone"* ]]; then
        echo "network"
    elif [[ $command == *"sudo"* ]] || [[ $exit_code -eq 126 ]] || [[ $exit_code -eq 13 ]]; then
        echo "permission"
    elif [[ $command == *"mkdir"* ]] || [[ $command == *"cp"* ]] || [[ $command == *"mv"* ]]; then
        echo "filesystem"
    elif [[ $exit_code -eq 127 ]]; then
        echo "command_not_found"
    elif [[ $exit_code -eq 124 ]]; then
        echo "timeout"
    else
        echo "general"
    fi
}

# Display user-friendly error message
display_error() {
    local error_type=$1
    local command=$2
    local line=$3

    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}❌ Installation Error Detected${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    case "$error_type" in
        package_manager)
            echo -e "${YELLOW}Type: Package Installation Failure${NC}"
            echo -e "${CYAN}Possible causes:${NC}"
            echo "  • Package not found in repository"
            echo "  • Repository not accessible"
            echo "  • Dependency conflict"
            echo -e "${GREEN}Suggested fixes:${NC}"
            echo "  1. Update package manager: brew update / sudo apt update"
            echo "  2. Check internet connection"
            echo "  3. Try installing manually: $command"
            ;;

        network)
            echo -e "${YELLOW}Type: Network Connection Error${NC}"
            echo -e "${CYAN}Possible causes:${NC}"
            echo "  • No internet connection"
            echo "  • Server is down"
            echo "  • Firewall blocking connection"
            echo -e "${GREEN}Suggested fixes:${NC}"
            echo "  1. Check internet connection"
            echo "  2. Try using a VPN"
            echo "  3. Check firewall settings"
            echo "  4. Retry the download manually"
            ;;

        permission)
            echo -e "${YELLOW}Type: Permission Denied${NC}"
            echo -e "${CYAN}Possible causes:${NC}"
            echo "  • Insufficient privileges"
            echo "  • File/directory ownership issues"
            echo -e "${GREEN}Suggested fixes:${NC}"
            echo "  1. Run with sudo: sudo $0"
            echo "  2. Check file permissions"
            echo "  3. Ensure you own the target directory"
            ;;

        filesystem)
            echo -e "${YELLOW}Type: File System Error${NC}"
            echo -e "${CYAN}Possible causes:${NC}"
            echo "  • Insufficient disk space"
            echo "  • Directory doesn't exist"
            echo "  • File already exists"
            echo -e "${GREEN}Suggested fixes:${NC}"
            echo "  1. Check disk space: df -h"
            echo "  2. Verify directory exists"
            echo "  3. Check file permissions"
            ;;

        command_not_found)
            echo -e "${YELLOW}Type: Command Not Found${NC}"
            echo -e "${CYAN}Missing command in:${NC} $command"
            echo -e "${GREEN}Suggested fixes:${NC}"
            echo "  1. Install missing dependency"
            echo "  2. Check PATH variable"
            echo "  3. Use full path to command"
            ;;

        timeout)
            echo -e "${YELLOW}Type: Operation Timeout${NC}"
            echo -e "${CYAN}Command took too long:${NC} $command"
            echo -e "${GREEN}Suggested fixes:${NC}"
            echo "  1. Increase timeout duration"
            echo "  2. Check system resources"
            echo "  3. Try operation again"
            ;;

        *)
            echo -e "${YELLOW}Type: General Error${NC}"
            echo -e "${CYAN}Failed command:${NC} $command"
            echo -e "${CYAN}At line:${NC} $line"
            ;;
    esac

    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${MAGENTA}Full error details saved to: $ERROR_LOG${NC}"
}

# Attempt automatic recovery
attempt_recovery() {
    local error_type=$1
    local command=$2

    log_info "Attempting automatic recovery for $error_type error..."

    case "$error_type" in
        package_manager)
            # Try alternative package manager or skip optional package
            if [[ $command == *"brew"* ]]; then
                log_info "Attempting to fix Homebrew..."
                brew doctor 2>/dev/null || true
                brew update 2>/dev/null || true
                # Retry original command
                eval "$command" 2>/dev/null && return 0
            fi
            ;;

        network)
            # Retry with exponential backoff
            local max_retries=3
            local retry=0
            local wait_time=2

            while [[ $retry -lt $max_retries ]]; do
                log_info "Retry attempt $((retry + 1))/$max_retries..."
                sleep "$wait_time"

                if eval "$command" 2>/dev/null; then
                    return 0
                fi

                wait_time=$((wait_time * 2))
                retry=$((retry + 1))
            done
            ;;

        permission)
            # Try with sudo if not already
            if [[ $command != *"sudo"* ]]; then
                log_info "Retrying with sudo..."
                if sudo $command 2>/dev/null; then
                    return 0
                fi
            fi
            ;;

        filesystem)
            # Check and free disk space if needed
            local available=$(df / | awk 'NR==2 {print $4}')
            if [[ $available -lt 1000000 ]]; then  # Less than 1GB
                log_warning "Low disk space detected"
                # Try to clean up
                cleanup_temp_files
                # Retry command
                eval "$command" 2>/dev/null && return 0
            fi
            ;;
    esac

    return 1
}

# Perform rollback
perform_rollback() {
    echo -e "${YELLOW}🔄 Starting rollback...${NC}"

    # Create rollback log
    local rollback_log="logs/rollback_$(date +%Y%m%d_%H%M%S).log"

    # Uninstall packages in reverse order
    for ((i=${#INSTALLED_PACKAGES[@]}-1; i>=0; i--)); do
        local pkg="${INSTALLED_PACKAGES[$i]}"
        echo "  Removing $pkg..."
        if command -v brew &>/dev/null; then
            brew uninstall "$pkg" 2>/dev/null || true
        elif command -v apt &>/dev/null; then
            sudo apt remove -y "$pkg" 2>/dev/null || true
        fi
        echo "Removed: $pkg" >> "$rollback_log"
    done

    # Restore modified files
    for file in "${MODIFIED_FILES[@]}"; do
        local backup="$BACKUP_DIR/$(basename "$file")"
        if [[ -f "$backup" ]]; then
            echo "  Restoring $file..."
            cp "$backup" "$file"
            echo "Restored: $file" >> "$rollback_log"
        fi
    done

    # Remove created directories
    for dir in "${CREATED_DIRS[@]}"; do
        echo "  Removing $dir..."
        rm -rf "$dir"
        echo "Removed directory: $dir" >> "$rollback_log"
    done

    echo -e "${GREEN}✅ Rollback completed${NC}"
    echo "Rollback details saved to: $rollback_log"
}

# Generate detailed error report
generate_error_report() {
    local exit_code=$1
    local line=$2
    local command=$3
    local error_type=$4

    local report_file="logs/error_report_$(date +%Y%m%d_%H%M%S).md"

    cat > "$report_file" << EOF
# Error Report

## Summary
- **Date**: $(date)
- **Script**: $0
- **Error Type**: $error_type
- **Exit Code**: $exit_code
- **Line Number**: $line
- **Failed Command**: \`$command\`

## System Information
- **OS**: $(uname -s)
- **Version**: $(uname -r)
- **Architecture**: $(uname -m)
- **Hostname**: $(hostname)
- **User**: $(whoami)

## Environment
\`\`\`
PATH=$PATH
HOME=$HOME
SHELL=$SHELL
\`\`\`

## Disk Space
\`\`\`
$(df -h)
\`\`\`

## Memory Usage
\`\`\`
$(free -h 2>/dev/null || vm_stat 2>/dev/null || echo "N/A")
\`\`\`

## Error Stack Trace
\`\`\`
$(cat "$ERROR_LOG")
\`\`\`

## Installed Packages Before Error
${INSTALLED_PACKAGES[@]:-None}

## Modified Files
${MODIFIED_FILES[@]:-None}

## Recommendations
$(get_recommendations "$error_type")

---
Generated by Speedy App Installer Error Handler
EOF

    echo -e "${MAGENTA}📄 Detailed error report saved to: $report_file${NC}"
}

# Get recommendations based on error type
get_recommendations() {
    local error_type=$1

    case "$error_type" in
        package_manager)
            echo "1. Update your package manager"
            echo "2. Check package name spelling"
            echo "3. Verify package availability for your OS"
            echo "4. Try manual installation"
            ;;
        network)
            echo "1. Check internet connectivity"
            echo "2. Verify DNS settings"
            echo "3. Try using a different network"
            echo "4. Check proxy settings"
            ;;
        permission)
            echo "1. Run installer with sudo"
            echo "2. Check directory ownership"
            echo "3. Verify user permissions"
            echo "4. Check SELinux/AppArmor policies"
            ;;
        *)
            echo "1. Check system resources"
            echo "2. Review installation logs"
            echo "3. Try running in verbose mode"
            echo "4. Contact support with error report"
            ;;
    esac
}

# Cleanup handler
cleanup_handler() {
    local exit_code=$?

    if [[ $exit_code -eq 0 ]]; then
        log_success "Installation completed successfully"
        # Clean up backup directory if successful
        [[ -d "$BACKUP_DIR" ]] && rm -rf "$BACKUP_DIR"
    else
        log_error "Installation failed with exit code: $exit_code"
    fi

    # Clean up temporary files
    cleanup_temp_files
}

# Interrupt handler
interrupt_handler() {
    echo -e "\n${YELLOW}⚠️  Installation interrupted by user${NC}"
    log_warning "Installation interrupted by user (SIGINT/SIGTERM)"

    if prompt_user "Do you want to rollback changes?"; then
        perform_rollback
    fi

    exit $ERR_USER_ABORT
}

# Cleanup temporary files
cleanup_temp_files() {
    log_info "Cleaning up temporary files..."

    # Clean common temp locations
    rm -rf /tmp/installer_* 2>/dev/null || true
    rm -rf /tmp/download_* 2>/dev/null || true

    # Clean Homebrew cache if on macOS
    if command -v brew &>/dev/null; then
        brew cleanup -s 2>/dev/null || true
    fi

    # Clean APT cache if on Linux
    if command -v apt &>/dev/null; then
        sudo apt autoclean 2>/dev/null || true
    fi
}

# Safe command execution with error handling
safe_execute() {
    local command=$1
    local description=${2:-"Executing command"}

    log_info "$description"

    if eval "$command"; then
        log_success "$description - Success"
        return 0
    else
        local exit_code=$?
        log_error "$description - Failed with exit code $exit_code"
        return $exit_code
    fi
}

# Track installed package
track_package() {
    local package=$1
    INSTALLED_PACKAGES+=("$package")
    echo "$(date): Installed $package" >> "$ERROR_LOG"
}

# Track modified file
track_file() {
    local file=$1

    # Backup original file if it exists
    if [[ -f "$file" ]]; then
        mkdir -p "$BACKUP_DIR"
        cp "$file" "$BACKUP_DIR/$(basename "$file")"
        MODIFIED_FILES+=("$file")
        echo "$(date): Modified $file (backup in $BACKUP_DIR)" >> "$ERROR_LOG"
    fi
}

# Track created directory
track_directory() {
    local dir=$1
    CREATED_DIRS+=("$dir")
    echo "$(date): Created directory $dir" >> "$ERROR_LOG"
}

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
    echo "$(date) [INFO]: $1" >> "$ERROR_LOG"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
    echo "$(date) [SUCCESS]: $1" >> "$ERROR_LOG"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    echo "$(date) [WARNING]: $1" >> "$ERROR_LOG"
}

log_error() {
    echo -e "${RED}❌ $1${NC}" >&2
    echo "$(date) [ERROR]: $1" >> "$ERROR_LOG"
}

# Prompt user for yes/no
prompt_user() {
    local prompt=$1
    local response

    while true; do
        read -p "$(echo -e "${CYAN}$prompt (y/n): ${NC}")" response
        case "$response" in
            [Yy]* ) return 0;;
            [Nn]* ) return 1;;
            * ) echo "Please answer yes (y) or no (n)";;
        esac
    done
}

# Check prerequisites with detailed reporting
check_prerequisites() {
    local missing_deps=()

    log_info "Checking prerequisites..."

    # Check required commands
    local required_commands=("curl" "git" "make")
    for cmd in "${required_commands[@]}"; do
        if ! command -v "$cmd" &>/dev/null; then
            missing_deps+=("$cmd")
        fi
    done

    # Check disk space (require at least 5GB)
    local available_space=$(df / | awk 'NR==2 {print $4}')
    if [[ $available_space -lt 5000000 ]]; then
        log_warning "Low disk space: $(df -h / | awk 'NR==2 {print $4}') available"
        log_warning "At least 5GB recommended"
    fi

    # Check internet connection
    if ! ping -c 1 google.com &>/dev/null && ! ping -c 1 1.1.1.1 &>/dev/null; then
        log_error "No internet connection detected"
        return $ERR_NETWORK
    fi

    # Report missing dependencies
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        log_error "Missing required dependencies: ${missing_deps[*]}"
        log_info "Please install them before continuing"
        return $ERR_DEPENDENCY
    fi

    log_success "All prerequisites met"
    return 0
}

# Validate installation
validate_installation() {
    local package=$1
    local validation_command=${2:-"command -v $package"}

    if eval "$validation_command" &>/dev/null; then
        log_success "$package installed successfully"
        return 0
    else
        log_error "$package installation verification failed"
        return 1
    fi
}

# Export functions for use in other scripts
export -f initialize_error_handler
export -f safe_execute
export -f track_package
export -f track_file
export -f track_directory
export -f log_info
export -f log_success
export -f log_warning
export -f log_error
export -f prompt_user
export -f check_prerequisites
export -f validate_installation