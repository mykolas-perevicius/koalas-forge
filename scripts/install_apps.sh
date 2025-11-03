#!/usr/bin/env bash
# App installation script

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/utils.sh"

LOG_DIR="../logs"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="${LOG_DIR}/install_${TIMESTAMP}.log"

mkdir -p "$LOG_DIR"

# Install a single app
install_app() {
    local name="$1"
    local package="$2"
    local install_type="$3"
    
    log_info "Installing: $name"
    
    # Skip null packages (manual install)
    if [[ "$package" == "null" ]] || [[ -z "$package" ]]; then
        log_warning "$name requires manual installation"
        return 0
    fi
    
    case "$install_type" in
        brew)
            if brew list "$package" &>/dev/null; then
                log_success "$name already installed"
            else
                if brew install "$package" >> "$LOG_FILE" 2>&1; then
                    log_success "$name installed"
                else
                    log_error "$name installation failed"
                    add_failure "$name"
                    return 1
                fi
            fi
            ;;

        cask)
            if brew list --cask "$package" &>/dev/null; then
                log_success "$name already installed"
            else
                if brew install --cask "$package" >> "$LOG_FILE" 2>&1; then
                    log_success "$name installed"
                else
                    log_error "$name installation failed"
                    add_failure "$name"
                    return 1
                fi
            fi
            ;;
            
        tap)
            local tap_name="$4"
            brew tap "$tap_name"
            install_app "$name" "$package" "brew"
            ;;
            
        *)
            log_error "Unknown install type: $install_type"
            return 1
            ;;
    esac
    
    return 0
}

# Install category
install_category() {
    local category="$1"
    
    log_section "Installing ${category} apps"
    
    case "$category" in
        ai_local)
            install_app "Ollama" "ollama" "brew"
            install_app "LM Studio" "lm-studio" "cask"
            install_app "GPT4All" "gpt4all" "cask"
            install_app "Jan" "jan" "cask"
            ;;
            
        development_core)
            install_app "Git" "git" "brew"
            install_app "Python 3.11" "python@3.11" "brew"
            install_app "Node.js" "node" "brew"
            install_app "Rust" "rust" "brew"
            install_app "Go" "go" "brew"
            install_app "Docker" "docker" "cask"
            ;;
            
        development_tools)
            install_app "Visual Studio Code" "visual-studio-code" "cask"
            install_app "Cursor" "cursor" "cask"
            install_app "Neovim" "neovim" "brew"
            install_app "GitHub Desktop" "github" "cask"
            install_app "Postman" "postman" "cask"
            install_app "Insomnia" "insomnia" "cask"
            install_app "TablePlus" "tableplus" "cask"
            ;;
            
        databases)
            install_app "PostgreSQL" "postgresql@16" "brew"
            install_app "MySQL" "mysql" "brew"
            install_app "Redis" "redis" "brew"
            ;;
            
        gaming)
            install_app "Steam" "steam" "cask"
            install_app "Discord" "discord" "cask"
            install_app "OBS Studio" "obs" "cask"
            ;;
            
        creative)
            install_app "Blender" "blender" "cask"
            install_app "GIMP" "gimp" "cask"
            install_app "Inkscape" "inkscape" "cask"
            ;;
            
        audio)
            install_app "Spotify" "spotify" "cask"
            install_app "Audacity" "audacity" "cask"
            ;;
            
        security)
            install_app "1Password" "1password" "cask"
            install_app "Bitwarden" "bitwarden" "cask"
            install_app "Wireshark" "wireshark" "cask"
            ;;
            
        productivity)
            install_app "Obsidian" "obsidian" "cask"
            install_app "Notion" "notion" "cask"
            if [[ "$(detect_platform)" == "mac" ]]; then
                install_app "Rectangle" "rectangle" "cask"
                install_app "Raycast" "raycast" "cask"
            fi
            ;;
            
        *)
            log_error "Unknown category: $category"
            return 1
            ;;
    esac
}

# Install all categories
install_all() {
    log_section "Starting Full Installation"
    
    install_category "ai_local"
    install_category "development_core"
    install_category "development_tools"
    install_category "databases"
    install_category "gaming"
    install_category "creative"
    install_category "audio"
    install_category "security"
    install_category "productivity"
    
    report_failures
}

export -f install_app install_category install_all
