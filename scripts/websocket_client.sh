#!/usr/bin/env bash

# WebSocket client for sending installation progress to GUI
# Uses curl or nc to send updates to the web interface

# WebSocket server details
WS_HOST="${WS_HOST:-localhost}"
WS_PORT="${WS_PORT:-8765}"
WS_URL="ws://${WS_HOST}:${WS_PORT}"

# Check if web GUI is running
check_gui_running() {
    curl -s "http://${WS_HOST}:8080/api/status" &>/dev/null
    return $?
}

# Send message to WebSocket server using curl
send_ws_message() {
    local message="$1"
    local level="${2:-info}"

    # Create JSON payload
    local json_payload=$(cat <<EOF
{
    "type": "output",
    "content": "$message",
    "level": "$level",
    "source": "terminal",
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
    )

    # Try to send via curl (if GUI is running)
    if check_gui_running; then
        # Use Python to send WebSocket message (most reliable)
        python3 -c "
import asyncio
import websockets
import json
import sys

async def send():
    try:
        async with websockets.connect('${WS_URL}') as ws:
            await ws.send('''${json_payload}''')
            return True
    except:
        return False

result = asyncio.run(send())
sys.exit(0 if result else 1)
" 2>/dev/null

        return $?
    fi

    return 1
}

# Send progress update
send_progress() {
    local percentage=$1
    local message="${2:-Installing...}"

    local json=$(cat <<EOF
{
    "type": "progress",
    "value": $percentage,
    "message": "$message",
    "source": "terminal"
}
EOF
    )

    if check_gui_running; then
        python3 -c "
import asyncio
import websockets

async def send():
    try:
        async with websockets.connect('${WS_URL}') as ws:
            await ws.send('''${json}''')
    except:
        pass

asyncio.run(send())
" 2>/dev/null
    fi
}

# Send installation statistics
send_stats() {
    local installed=$1
    local failed=$2
    local disk_used="${3:-0}"

    local json=$(cat <<EOF
{
    "type": "stats",
    "installed": $installed,
    "failed": $failed,
    "diskUsed": $disk_used,
    "source": "terminal"
}
EOF
    )

    if check_gui_running; then
        python3 -c "
import asyncio
import websockets

async def send():
    try:
        async with websockets.connect('${WS_URL}') as ws:
            await ws.send('''${json}''')
    except:
        pass

asyncio.run(send())
" 2>/dev/null
    fi
}

# Export functions
export -f check_gui_running
export -f send_ws_message
export -f send_progress
export -f send_stats