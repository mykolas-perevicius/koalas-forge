#!/usr/bin/env bash

# 🧪 Speedy App Installer - Test Suite
# Tests installation scripts and validates configuration

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test results
PASSED=0
FAILED=0
WARNINGS=0

# Log file
LOG_FILE="logs/test_$(date +%Y%m%d_%H%M%S).txt"
mkdir -p logs

# Test function
run_test() {
    local test_name="$1"
    local test_command="$2"

    echo -e "${BLUE}Testing:${NC} $test_name"

    if eval "$test_command" >> "$LOG_FILE" 2>&1; then
        echo -e "  ${GREEN}✅ PASSED${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "  ${RED}❌ FAILED${NC}"
        ((FAILED++))
        return 1
    fi
}

# Warning function
check_warning() {
    local check_name="$1"
    local check_command="$2"

    echo -e "${YELLOW}Checking:${NC} $check_name"

    if eval "$check_command" >> "$LOG_FILE" 2>&1; then
        echo -e "  ${GREEN}✓ OK${NC}"
        return 0
    else
        echo -e "  ${YELLOW}⚠️  WARNING${NC}"
        ((WARNINGS++))
        return 1
    fi
}

# Header
echo "═══════════════════════════════════════════════════════"
echo "    🧪 SPEEDY APP INSTALLER - TEST SUITE               "
echo "═══════════════════════════════════════════════════════"
echo ""
echo "Log file: $LOG_FILE"
echo ""

# Test 1: Check if main script exists and is executable
run_test "Main installer script exists" "test -f install.sh"
run_test "Main installer is executable" "test -x install.sh"

# Test 2: Check all required scripts
echo ""
echo "📁 Checking required scripts..."
run_test "Hardware detection script exists" "test -f scripts/detect_hardware.sh"
run_test "App installer script exists" "test -f scripts/install_apps.sh"
run_test "AI setup script exists" "test -f scripts/setup_ai.sh"
run_test "System optimizer exists" "test -f scripts/optimize_system.sh"
run_test "Driver installer exists" "test -f scripts/install_drivers.sh"
run_test "Utils script exists" "test -f scripts/utils.sh"

# Test 3: Check configuration files
echo ""
echo "📋 Checking configuration files..."
run_test "Apps configuration exists" "test -f apps.yaml"
run_test "Apps configuration is valid YAML" "python3 -c 'import yaml; yaml.safe_load(open(\"apps.yaml\"))' 2>/dev/null || ruby -ryaml -e 'YAML.load_file(\"apps.yaml\")'"
check_warning "AI config exists" "test -f configs/ai-config.yaml"
check_warning "Dev config exists" "test -f configs/dev-config.yaml"

# Test 4: Check bash syntax
echo ""
echo "🔍 Validating bash syntax..."
for script in install.sh scripts/*.sh; do
    if [ -f "$script" ]; then
        run_test "Syntax check: $(basename $script)" "bash -n $script"
    fi
done

# Test 5: Check dependencies
echo ""
echo "🔧 Checking system dependencies..."
run_test "Bash version >= 3.2" "bash -c '[[ ${BASH_VERSION%%.*} -ge 3 ]]'"
check_warning "Git is installed" "command -v git"
check_warning "curl is installed" "command -v curl"
check_warning "Python is installed" "command -v python3"

# Test 6: Check for Homebrew (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo ""
    echo "🍺 Checking macOS dependencies..."
    check_warning "Homebrew is installed" "command -v brew"
    check_warning "Xcode Command Line Tools" "xcode-select -p"
fi

# Test 7: Dry run tests
echo ""
echo "🏃 Testing dry-run modes..."
run_test "Dry run help command" "./install.sh --help 2>/dev/null | grep -q 'Usage'"
run_test "Detect hardware dry run" "./scripts/detect_hardware.sh 2>/dev/null"

# Test 8: Check directory structure
echo ""
echo "📂 Validating directory structure..."
run_test "Logs directory exists" "test -d logs"
run_test "Scripts directory exists" "test -d scripts"
run_test "Configs directory exists" "test -d configs"

# Test 9: Check Git repository
echo ""
echo "📝 Checking version control..."
run_test "Git repository exists" "test -d .git"
run_test "Git has commits" "git log --oneline -1"
check_warning "No uncommitted changes" "git diff --quiet && git diff --cached --quiet"

# Test 10: Installation simulation
echo ""
echo "🚀 Testing installation simulation..."
if [[ "$1" == "--full-test" ]]; then
    echo "Running full installation test (this may take time)..."
    run_test "Minimal install dry-run" "./install.sh --minimal --dry-run --no-sync"
else
    echo "Skipping full test (use --full-test to enable)"
fi

# Test 11: Check documentation
echo ""
echo "📚 Checking documentation..."
run_test "README exists" "test -f README.md"
run_test "Work log exists" "test -f WORK_LOG.md"
run_test "Next steps exists" "test -f NEXT_STEPS.md"

# Test 12: Performance checks
echo ""
echo "⚡ Performance checks..."
run_test "Script size reasonable" "[ $(wc -l < install.sh) -lt 1000 ]"
run_test "Apps list not empty" "grep -q 'apps:' apps.yaml"

# Results Summary
echo ""
echo "═══════════════════════════════════════════════════════"
echo "    📊 TEST RESULTS SUMMARY                            "
echo "═══════════════════════════════════════════════════════"
echo ""
echo -e "  ${GREEN}Passed:${NC}   $PASSED"
echo -e "  ${RED}Failed:${NC}   $FAILED"
echo -e "  ${YELLOW}Warnings:${NC} $WARNINGS"
echo ""

# Overall status
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    echo "The installer appears to be ready for use."
    exit 0
else
    echo -e "${RED}❌ Some tests failed.${NC}"
    echo "Please review the log file: $LOG_FILE"
    exit 1
fi