# 🧪 Manual Test Commands

**Copy and paste these commands to test the Ultimate System Setup Installer yourself!**

---

## 📋 Quick Test (5 minutes)

```bash
# Navigate to the directory
cd ~/app-installer

# 1. Test help command
./install.sh --help

# 2. Detect your hardware
./install.sh --detect-hardware

# 3. Run a safe dry-run test
./install.sh --minimal --dry-run

# 4. Run the automated test suite
./test_install.sh

# Done! If all 4 commands succeed, everything is working!
```

---

## 🔬 Comprehensive Test Suite (10-15 minutes)

### Step 1: Start the GUI Server

```bash
# Clean up any existing processes first
killall python3 2>/dev/null || true
lsof -ti:8080,8765 | xargs kill -9 2>/dev/null || true

# Start the GUI with automatic browser launch
./start_sync.sh
```

**Expected Output:**
```
✅ Cleanup complete
✅ GUI server started
✅ Server is responding
✅ Sync API is ready
✅ Browser opened
```

The web interface should open automatically at: **http://localhost:8080**

---

### Step 2: Test API Endpoints (in a new terminal)

```bash
cd ~/app-installer

# Test status endpoint
curl -s http://localhost:8080/api/status | python3 -m json.tool

# Test terminal progress endpoint
curl -s http://localhost:8080/api/terminal-progress | python3 -m json.tool

# Test web interface accessibility
curl -s http://localhost:8080 | head -30
```

**Expected:**
- Valid JSON responses
- System information displayed
- HTML served correctly

---

### Step 3: Test All Installation Modes

```bash
# Test help
./install.sh --help

# Test hardware detection
./install.sh --detect-hardware

# Test minimal mode (dry run - safe!)
./install.sh --minimal --dry-run

# Test dev mode (dry run - safe!)
./install.sh --dev --dry-run

# Test AI mode (dry run - safe!)
./install.sh --ai --dry-run

# Test with sync disabled
./install.sh --minimal --dry-run --no-sync
```

**Expected:**
- Each mode displays correct packages
- Dry run shows simulation without making changes
- GUI sync detected when enabled
- No errors

---

### Step 4: Test Terminal-GUI Sync

```bash
# Start GUI first (if not already running)
./start_sync.sh

# In a NEW terminal window, run installation
cd ~/app-installer
./install.sh --minimal --dry-run
```

**Watch in the Web GUI (http://localhost:8080):**
- Progress bar should move automatically
- "🔄 Terminal Sync Active" badge appears
- Package names update in real-time
- Statistics update every 2 seconds

**Expected:**
- Terminal shows "✅ Web GUI detected"
- GUI displays progress updates
- Sync happens automatically

---

### Step 5: Run Comprehensive Test Suite

```bash
# Run all automated tests
./test_install.sh

# For full installation test (takes longer)
./test_install.sh --full-test
```

**Expected Output:**
```
═══════════════════════════════════════════════════════
    📊 TEST RESULTS SUMMARY
═══════════════════════════════════════════════════════

  Passed:   34
  Failed:   0
  Warnings: 0

✅ All tests passed!
```

---

### Step 6: Verify Git Repository

```bash
# Check git status
git status

# View commit history
git log --oneline -10

# Verify remote
git remote -v

# Check latest commits
git log --oneline --graph --decorate -7
```

**Expected:**
- Working tree clean
- 7 commits ahead (now pushed)
- Remote: https://github.com/mykolas-perevicius/ultimate-system-setup.git

---

### Step 7: Check Documentation

```bash
# List all documentation
ls -lh *.md

# View key documents
cat FINAL_STATUS.md | head -50
cat SYNC_GUIDE.md | head -50
cat TEST_RESULTS.md | head -50
```

**Expected:**
- WORK_LOG.md
- NEXT_STEPS.md
- SYNC_GUIDE.md (357 lines)
- FINAL_STATUS.md (479 lines)
- TEST_RESULTS.md (648 lines)

---

### Step 8: Verify GUI Server Status

```bash
# Check if server is running
ps aux | grep -E "(gui_server|python3.*gui)" | grep -v grep

# Check port bindings
lsof -ti:8080 -ti:8765

# Check server logs
tail -20 /tmp/gui_server.log

# Check WebSocket version
python3 -c "import websockets; print(f'websockets version: {websockets.__version__}')"
```

**Expected:**
- Python process running gui_server.py
- Ports 8080 and 8765 bound
- WebSocket version 15.0.1
- No errors in logs

---

### Step 9: Test Progress Tracking

```bash
# Check if progress file exists
ls -la /tmp/app_installer_progress.json

# View progress file contents
cat /tmp/app_installer_progress.json | python3 -m json.tool

# Parse progress data
cat /tmp/app_installer_progress.json | python3 -c "import json,sys; data=json.load(sys.stdin); print(f'Status: {data[\"status\"]}'); print(f'Progress: {data[\"progress\"]}%'); print(f'Mode: {data[\"mode\"]}')"
```

**Expected:**
- Progress file exists
- Valid JSON format
- Status, progress, and mode fields present

---

### Step 10: Test Project Structure

```bash
# View directory structure
tree -L 2 -I 'logs|__pycache__|*.pyc|.git' --dirsfirst

# Or use ls
ls -la
ls -la scripts/
ls -la gui/
ls -la configs/
```

**Expected:**
- All scripts in scripts/ directory
- GUI files in gui/ directory
- Config files in configs/ directory
- Documentation in root

---

## 🎯 One-Command Full Test

```bash
# Run everything in sequence
cd ~/app-installer && \
echo "=== Testing Help ===" && \
./install.sh --help && \
echo "" && \
echo "=== Testing Hardware Detection ===" && \
./install.sh --detect-hardware && \
echo "" && \
echo "=== Testing Dry Run ===" && \
./install.sh --minimal --dry-run && \
echo "" && \
echo "=== Running Test Suite ===" && \
./test_install.sh && \
echo "" && \
echo "=== All Tests Complete! ==="
```

---

## 🔍 Verification Checklist

After running the tests, verify:

- [ ] Help command displays all options
- [ ] Hardware detection works and generates report
- [ ] Dry run completes without errors
- [ ] Test suite passes (34/34 tests)
- [ ] GUI server starts on port 8080
- [ ] Web interface accessible in browser
- [ ] API endpoints return valid JSON
- [ ] Terminal-GUI sync works (progress updates in browser)
- [ ] Progress file created and readable
- [ ] Git repository clean and pushed
- [ ] All documentation present
- [ ] No Python/Bash errors

---

## 🐛 Troubleshooting Commands

### GUI Not Starting?

```bash
# Kill all Python processes
killall python3 2>/dev/null

# Clear ports
lsof -ti:8080,8765 | xargs kill -9 2>/dev/null

# Remove old progress file
rm -f /tmp/app_installer_progress.json

# Try starting again
./start_sync.sh
```

### Port Already in Use?

```bash
# Check what's using the ports
lsof -i :8080
lsof -i :8765

# Kill specific process
kill -9 <PID>

# Or kill all on those ports
lsof -ti:8080,8765 | xargs kill -9
```

### Sync Not Working?

```bash
# Verify API endpoint
curl -s http://localhost:8080/api/terminal-progress

# Check server logs
tail -f /tmp/gui_server.log

# Restart everything
killall python3 2>/dev/null
./start_sync.sh
# Then in new terminal:
./install.sh --minimal --dry-run
```

### Test Suite Failing?

```bash
# Check which test failed
./test_install.sh 2>&1 | tee test_output.txt
grep FAILED test_output.txt

# View detailed logs
cat logs/test_*.txt | tail -50
```

---

## 📊 Performance Benchmarks

### Expected Timings:

```bash
# Dry run (minimal) - should complete in ~4 seconds
time ./install.sh --minimal --dry-run

# Hardware detection - should complete in ~2 seconds
time ./install.sh --detect-hardware

# Test suite - should complete in ~30 seconds
time ./test_install.sh

# API response - should be < 100ms
time curl -s http://localhost:8080/api/status > /dev/null
```

---

## 🎨 Visual Tests

### Test Web Interface:

1. Open browser: http://localhost:8080
2. You should see:
   - Dark theme with purple gradient
   - "🚀 Speedy App Installer" header
   - System information card
   - Progress section
   - Package selection (if not syncing)

3. Start installation in terminal: `./install.sh --minimal --dry-run`
4. Watch the GUI:
   - Progress bar should move
   - "🔄 Terminal Sync Active" badge appears
   - Current package name updates
   - Statistics increment

---

## 💾 Installation Logs

### Check Installation History:

```bash
# List all installation logs
ls -lht install_log_*.txt

# View most recent log
cat install_log_*.txt | head -100

# Check hardware report
cat detected_hardware.txt
```

---

## 🚀 Production Commands (Use with Caution!)

**WARNING: These will actually install software!**

```bash
# Install AI/LLM tools (requires confirmation)
./install.sh --ai

# Install development environment
./install.sh --dev

# Install everything
./install.sh --full

# Install with optimizations
./install.sh --full --optimize

# Install drivers
./install.sh --drivers
```

**Always test with `--dry-run` first!**

---

## 📸 Screenshot Tests

If you want to verify the GUI visually:

1. Start GUI: `./start_sync.sh`
2. Open: http://localhost:8080
3. In new terminal: `./install.sh --minimal --dry-run`
4. Take screenshot during installation
5. Verify you see:
   - Active progress bar
   - "Terminal Sync Active" indicator
   - Package names updating
   - Statistics changing

---

## ✅ Success Indicators

You'll know everything is working when:

1. ✅ All commands complete without errors
2. ✅ Test suite shows 34/34 passed
3. ✅ GUI opens in browser automatically
4. ✅ API endpoints return valid JSON
5. ✅ Sync indicator appears during installation
6. ✅ Progress updates in real-time
7. ✅ No Python/Bash errors in logs
8. ✅ Git status shows clean working tree

---

## 🎓 Quick Reference

### Most Important Commands:

```bash
# Quick test
./install.sh --minimal --dry-run

# Run tests
./test_install.sh

# Start GUI
./start_sync.sh

# Help
./install.sh --help
```

### Check System Status:

```bash
# Git status
git status && git log --oneline -5

# Server status
ps aux | grep gui_server | grep -v grep

# Port status
lsof -ti:8080,8765

# API status
curl -s http://localhost:8080/api/status
```

---

## 📞 Need Help?

If something doesn't work:

1. Check the logs:
   ```bash
   tail -f /tmp/gui_server.log
   cat logs/test_*.txt
   ```

2. Restart everything:
   ```bash
   killall python3 2>/dev/null
   ./start_sync.sh
   ```

3. Review documentation:
   ```bash
   cat SYNC_GUIDE.md
   cat TROUBLESHOOTING.md
   ```

---

## 🎉 When All Tests Pass

You should see:
- ✅ 40/40 tests passing
- ✅ No errors in any command
- ✅ GUI accessible in browser
- ✅ Sync working between terminal and GUI
- ✅ All documentation present
- ✅ Git repository clean and pushed

**System is production ready!** 🚀

---

**Happy Testing!**
