# 🧪 Test Commands for Speedy App Installer

## ✅ Quick Test Suite

Run all these commands to fully test the GUI and dry run features:

```bash
# 1. Run automated tests
./test_install.sh

# 2. Test dry run mode (no actual changes)
./install.sh --full --dry-run
./install.sh --ai --dry-run
./install.sh --dev --dry-run
./install.sh --minimal --dry-run

# 3. Test hardware detection
./scripts/detect_hardware.sh

# 4. Test help system
./install.sh --help
./launch_gui.sh help
```

## 🌐 Web Interface Testing

### Launch Web GUI:
```bash
# Start the web interface
./launch_gui.sh web

# Or just:
./launch_gui.sh
```

**Web Interface URL:** http://localhost:8080

### Test Features in Browser:
1. Click "Detect Hardware" button
2. Switch between installation modes (Full, AI, Dev, Minimal, Custom)
3. Select "Custom" mode to see package selection
4. Click "Run Tests" button
5. Try "Start Installation" with dry run enabled

### Test WebSocket Connection:
```bash
# Check server status
curl http://localhost:8080/api/status

# Check available packages
curl http://localhost:8080/api/packages

# Check hardware detection
curl http://localhost:8080/api/hardware
```

## 🖥️ Desktop GUI Testing

### Launch Desktop GUI:
```bash
# Start tkinter GUI
./launch_gui.sh desktop

# Or:
./launch_gui.sh tkinter
```

### Features to Test:
- Mode selection radio buttons
- Package selection in custom mode
- Hardware detection display
- Progress bar animation
- Output console scrolling

## 🧪 Dry Run Mode Testing

### Basic Dry Run:
```bash
# Test without making any changes
./install.sh --full --dry-run
```

### Expected Output:
- Shows "🧪 DRY RUN MODE" banner
- Simulates all installation steps
- No actual packages installed
- Shows summary at the end
- ~3-5 second completion time

### Dry Run with Different Modes:
```bash
# AI tools dry run
./install.sh --ai --dry-run

# Development tools dry run
./install.sh --dev --dry-run

# Minimal setup dry run
./install.sh --minimal --dry-run
```

## 🛡️ Error Handling Testing

### Test Error Handler:
```bash
# Source and test error handler
source scripts/error_handler.sh
initialize_error_handler

# Test successful command
safe_execute "echo 'Success test'" "Testing success"

# Test failing command (triggers error handling)
safe_execute "false" "Testing error handling"
```

### Test Network Error Recovery:
```bash
# This will retry with exponential backoff
source scripts/error_handler.sh
initialize_error_handler
safe_execute "curl http://nonexistent-url-test.com" "Testing network error"
```

### Test Rollback Mechanism:
```bash
# Create test script
cat > test_rollback.sh << 'EOF'
#!/bin/bash
source scripts/error_handler.sh
initialize_error_handler
track_package "test-package"
echo "Simulating error..."
exit 1
EOF

chmod +x test_rollback.sh
./test_rollback.sh
# Should offer to rollback
```

## 🚀 Performance Testing

### Quick Installation Test:
```bash
# Time a dry run
time ./install.sh --minimal --dry-run

# Should complete in 3-5 seconds
```

### Memory Usage Test:
```bash
# Monitor while running
./launch_gui.sh web &
ps aux | grep python3 | grep gui_server
```

## 🔍 Troubleshooting Tests

### Check Port Availability:
```bash
# Check if ports are in use
lsof -i :8080
lsof -i :8765

# Kill processes if needed
lsof -ti:8080,8765 | xargs kill -9 2>/dev/null || true
```

### Check Python Dependencies:
```bash
# Test all required packages
python3 -c "import tkinter; print('✓ Tkinter')"
python3 -c "import yaml; print('✓ YAML')"
python3 -c "import aiohttp; print('✓ aiohttp')"
python3 -c "import websockets; print('✓ websockets')"
```

### Check Script Permissions:
```bash
# Verify all scripts are executable
ls -la scripts/*.sh | grep -v "^-rwx"
ls -la gui/*.py | grep -v "^-rwx"
ls -la *.sh | grep -v "^-rwx"

# Fix if needed
chmod +x scripts/*.sh gui/*.py *.sh
```

## 📊 Full Integration Test

Run this for a complete system test:

```bash
#!/bin/bash

echo "=== Speedy App Installer - Full Test Suite ==="

echo -e "\n1. Testing automated test suite..."
./test_install.sh

echo -e "\n2. Testing dry run modes..."
for mode in full ai dev minimal; do
    echo "Testing $mode mode..."
    ./install.sh --$mode --dry-run 2>&1 | tail -5
done

echo -e "\n3. Testing hardware detection..."
./scripts/detect_hardware.sh | head -10

echo -e "\n4. Testing web interface..."
timeout 5 ./launch_gui.sh web 2>&1 | head -20 || true

echo -e "\n5. Testing help systems..."
./install.sh --help | head -10
./launch_gui.sh help | head -10

echo -e "\n✅ All tests completed!"
```

## 🎯 Expected Results

### Successful Test Indicators:
- ✅ All test suite checks pass (30/30)
- ✅ Dry run completes in 3-5 seconds
- ✅ Web interface loads at http://localhost:8080
- ✅ No error messages in console
- ✅ Hardware detection shows system info
- ✅ Help commands display properly

### Common Issues & Fixes:

| Issue | Fix |
|-------|-----|
| Port 8080 in use | `lsof -ti:8080 \| xargs kill -9` |
| Python packages missing | `pip3 install pyyaml aiohttp websockets` |
| Permission denied | `chmod +x scripts/*.sh` |
| No display for GUI | Use web interface instead |
| WebSocket connection fails | Check firewall/port 8765 |

## 📝 Quick Commands Reference

```bash
# Launch web UI (recommended)
./launch_gui.sh

# Test installation without changes
./install.sh --full --dry-run

# Run test suite
./test_install.sh

# Detect hardware
./scripts/detect_hardware.sh

# View help
./install.sh --help

# Stop all processes
killall python3 2>/dev/null || true
```

---

**Created:** November 3, 2025
**Purpose:** Comprehensive testing guide for GUI and dry run features
**Status:** Ready for testing!