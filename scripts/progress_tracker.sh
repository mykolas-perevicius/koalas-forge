#!/usr/bin/env bash

# Progress Tracking System for Terminal-GUI Synchronization
# Creates a shared progress file that both terminal and web GUI can use

PROGRESS_FILE="/tmp/app_installer_progress.json"
LOCK_FILE="/tmp/app_installer.lock"

# Initialize progress tracking
init_progress() {
    local mode="${1:-unknown}"

    cat > "$PROGRESS_FILE" << EOF
{
    "status": "running",
    "mode": "$mode",
    "start_time": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "progress": 0,
    "current_package": "",
    "packages_installed": [],
    "packages_failed": [],
    "messages": [],
    "stats": {
        "installed": 0,
        "failed": 0,
        "total": 0,
        "disk_used": 0
    }
}
EOF

    echo -e "${CYAN}📊 Progress tracking initialized${NC}"
    echo -e "${BLUE}  Web GUI can monitor: $PROGRESS_FILE${NC}"
}

# Update progress percentage
update_progress() {
    local percentage=$1
    local message="${2:-}"

    if [[ -f "$PROGRESS_FILE" ]]; then
        # Simple file lock without flock (macOS compatible)
        (

            # Read current state
            local current=$(cat "$PROGRESS_FILE" 2>/dev/null || echo "{}")

            # Update with Python for proper JSON handling
            python3 -c "
import json
import sys

data = json.loads('''$current''')
data['progress'] = $percentage
if '$message':
    data['current_package'] = '$message'
    if 'messages' not in data:
        data['messages'] = []
    data['messages'].append({
        'time': '$(date -u +%Y-%m-%dT%H:%M:%SZ)',
        'message': '$message',
        'progress': $percentage
    })

print(json.dumps(data, indent=2))
" > "$PROGRESS_FILE.tmp" && mv "$PROGRESS_FILE.tmp" "$PROGRESS_FILE"

        )
    fi

    # Also try to send via WebSocket if GUI is running
    if [[ -f "./scripts/websocket_client.sh" ]]; then
        source "./scripts/websocket_client.sh"
        send_progress "$percentage" "$message" 2>/dev/null || true
    fi
}

# Track package installation
track_package() {
    local package=$1
    local status=$2  # "success" or "failed"

    if [[ -f "$PROGRESS_FILE" ]]; then
        (

            python3 -c "
import json

data = json.loads(open('$PROGRESS_FILE').read())

if '$status' == 'success':
    if 'packages_installed' not in data:
        data['packages_installed'] = []
    data['packages_installed'].append('$package')
    data['stats']['installed'] = len(data['packages_installed'])
else:
    if 'packages_failed' not in data:
        data['packages_failed'] = []
    data['packages_failed'].append('$package')
    data['stats']['failed'] = len(data['packages_failed'])

with open('$PROGRESS_FILE', 'w') as f:
    json.dump(data, f, indent=2)
" 2>/dev/null || true

        )
    fi

    # Send to WebSocket
    if [[ -f "./scripts/websocket_client.sh" ]]; then
        source "./scripts/websocket_client.sh"
        if [[ "$status" == "success" ]]; then
            send_ws_message "✅ Installed: $package" "success" 2>/dev/null || true
        else
            send_ws_message "❌ Failed: $package" "error" 2>/dev/null || true
        fi
    fi
}

# Complete progress tracking
complete_progress() {
    local status="${1:-completed}"  # "completed" or "failed"

    if [[ -f "$PROGRESS_FILE" ]]; then
        (

            python3 -c "
import json

data = json.loads(open('$PROGRESS_FILE').read())
data['status'] = '$status'
data['end_time'] = '$(date -u +%Y-%m-%dT%H:%M:%SZ)'
data['progress'] = 100 if '$status' == 'completed' else data.get('progress', 0)

with open('$PROGRESS_FILE', 'w') as f:
    json.dump(data, f, indent=2)
" 2>/dev/null || true

        )
    fi

    # Clean up lock file
    rm -f "$LOCK_FILE"
}

# Get current progress (for GUI to poll)
get_progress() {
    if [[ -f "$PROGRESS_FILE" ]]; then
        cat "$PROGRESS_FILE"
    else
        echo '{"status": "idle", "progress": 0}'
    fi
}

# Terminal progress bar
show_progress_bar() {
    local percentage=$1
    local width=50
    local filled=$((percentage * width / 100))
    local empty=$((width - filled))

    printf "\r["
    printf "%${filled}s" | tr ' ' '█'
    printf "%${empty}s" | tr ' ' '░'
    printf "] %3d%%" "$percentage"
}

# Export functions
export -f init_progress
export -f update_progress
export -f track_package
export -f complete_progress
export -f get_progress
export -f show_progress_bar

# Colors for output
export CYAN='\033[0;36m'
export BLUE='\033[0;34m'
export GREEN='\033[0;32m'
export YELLOW='\033[1;33m'
export RED='\033[0;31m'
export NC='\033[0m'