#!/usr/bin/env bash
# Setup local AI/LLM infrastructure

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/utils.sh"

AI_DIR="../ai-models"
mkdir -p "$AI_DIR"

setup_ollama() {
    log_section "Setting up Ollama"
    
    # Install Ollama if needed
    if ! command_exists ollama; then
        brew install ollama
    fi
    
    # Start Ollama service
    ollama serve > /dev/null 2>&1 &
    sleep 5
    
    # Pull models
    log_info "Pulling AI models (this takes time)..."
    
    models=(
        "llama3.2:latest"
        "mistral:latest"
        "codellama:latest"
        "phi3:latest"
        "gemma2:2b"
    )
    
    for model in "${models[@]}"; do
        log_info "Pulling $model..."
        ollama pull "$model" || log_warning "Failed: $model"
    done
    
    log_success "Ollama setup complete"
    log_info "Run: ollama run llama3.2"
}

setup_comfyui() {
    log_section "Setting up ComfyUI"
    
    if [[ ! -d "$AI_DIR/ComfyUI" ]]; then
        cd "$AI_DIR"
        git clone https://github.com/comfyanonymous/ComfyUI.git
        cd ComfyUI
        
        # Create venv and install
        python3 -m venv venv
        source venv/bin/activate
        pip install torch torchvision torchaudio
        pip install -r requirements.txt
        
        log_success "ComfyUI installed"
        log_info "Start: cd $AI_DIR/ComfyUI && python main.py"
    fi
}

setup_text_gen_webui() {
    log_section "Setting up Text Generation WebUI"
    
    if [[ ! -d "$AI_DIR/text-generation-webui" ]]; then
        cd "$AI_DIR"
        git clone https://github.com/oobabooga/text-generation-webui.git
        cd text-generation-webui
        
        # Install based on platform
        if [[ "$(detect_platform)" == "mac" ]]; then
            if [[ -f "start_macos.sh" ]]; then
                bash start_macos.sh --help
            fi
        elif [[ "$(detect_platform)" == "linux" ]]; then
            if [[ -f "start_linux.sh" ]]; then
                bash start_linux.sh --help
            fi
        fi
        
        log_success "Text Gen WebUI installed"
    fi
}

install_python_ai_packages() {
    log_section "Installing AI Python Packages"
    
    packages=(
        "torch"
        "transformers"
        "accelerate"
        "diffusers"
        "langchain"
        "chromadb"
        "openai"
        "anthropic"
        "gradio"
        "streamlit"
    )
    
    for pkg in "${packages[@]}"; do
        log_info "Installing $pkg..."
        pip install --upgrade "$pkg" 2>/dev/null || log_warning "Failed: $pkg"
    done
    
    log_success "Python AI packages installed"
}

check_gpu() {
    log_section "GPU Check for AI"
    
    local gpu_type=$(check_gpu)
    
    case "$gpu_type" in
        apple_silicon)
            log_success "Apple Silicon detected - Metal acceleration available"
            log_info "Optimal for MLX models"
            ;;
        nvidia)
            log_success "NVIDIA GPU detected"
            nvidia-smi --query-gpu=name,memory.total --format=csv,noheader || true
            ;;
        amd)
            log_info "AMD GPU detected - ROCm support possible"
            ;;
        *)
            log_warning "No GPU detected - CPU inference only"
            ;;
    esac
}

main() {
    log_section "AI/LLM Infrastructure Setup"
    
    check_gpu
    install_python_ai_packages
    setup_ollama
    setup_comfyui
    setup_text_gen_webui
    
    log_section "AI Setup Complete!"
    echo ""
    log_info "🤖 Quick Start:"
    echo "  Chat: ollama run llama3.2"
    echo "  Image: cd ~/app-installer/ai-models/ComfyUI && python main.py"
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main
fi
