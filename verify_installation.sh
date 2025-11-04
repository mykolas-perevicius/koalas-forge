#!/bin/bash
#
# 🐨 Koala's Forge - Installation Verification Script
# Checks that everything is set up correctly
#

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║        🐨 KOALA'S FORGE - INSTALLATION VERIFICATION         ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

CHECKS_PASSED=0
CHECKS_FAILED=0

# Function to check something
check() {
    local description="$1"
    local command="$2"

    printf "%-50s" "Checking $description..."

    if eval "$command" &>/dev/null; then
        echo -e "${GREEN}✓${NC}"
        ((CHECKS_PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC}"
        ((CHECKS_FAILED++))
        return 1
    fi
}

echo -e "${YELLOW}📋 Running verification checks...${NC}\n"

# Core files
check "launch.sh exists" "test -f launch.sh"
check "launch.sh is executable" "test -x launch.sh"
check "apps.yaml exists" "test -f apps.yaml"
check "README.md exists" "test -f README.md"
check "QUICKSTART.md exists" "test -f QUICKSTART.md"
check "CONTRIBUTING.md exists" "test -f CONTRIBUTING.md"
check "CHANGELOG.md exists" "test -f CHANGELOG.md"

# GUI files
check "Web interface exists" "test -f gui/koalas_forge.html"
check "Server script exists" "test -f gui/koalas_forge_server.py"
check "Server is executable" "test -x gui/koalas_forge_server.py"
check "Lite GUI exists" "test -f gui/koalas_forge_lite.py"

# Directories
check "logs directory exists" "test -d logs"
check "configs directory exists" "test -d configs"
check "scripts directory exists" "test -d scripts"
check "gui directory exists" "test -d gui"
check "tests directory exists" "test -d tests"
check "demo directory exists" "test -d demo"

# Dependencies
check "Python 3 installed" "command -v python3"
check "Git installed" "command -v git"

# Python packages
check "aiohttp installed" "python3 -c 'import aiohttp'"
check "websockets installed" "python3 -c 'import websockets'"
check "yaml installed" "python3 -c 'import yaml'"

# Optional dependencies
if check "Homebrew installed" "command -v brew"; then
    echo -e "  ${BLUE}ℹ${NC}  Homebrew version: $(brew --version | head -1)"
fi

if check "Playwright installed" "python3 -c 'import playwright'"; then
    echo -e "  ${BLUE}ℹ${NC}  Playwright available for testing"
fi

# Check apps.yaml validity
echo ""
printf "%-50s" "Validating apps.yaml structure..."
if python3 -c "
import yaml
import sys

try:
    with open('apps.yaml', 'r') as f:
        data = yaml.safe_load(f)

    assert 'apps' in data, 'Missing apps key'

    # Check each app has required fields
    required = ['name', 'package', 'platforms', 'install_type']
    for category, apps in data['apps'].items():
        for app in apps:
            for field in required:
                assert field in app, f'App missing {field}'

    sys.exit(0)
except Exception as e:
    print(f'Error: {e}', file=sys.stderr)
    sys.exit(1)
" 2>/dev/null; then
    echo -e "${GREEN}✓${NC}"
    ((CHECKS_PASSED++))
else
    echo -e "${RED}✗${NC}"
    ((CHECKS_FAILED++))
fi

# Check for koala branding
echo ""
printf "%-50s" "Checking Koala branding in README..."
if grep -q "Koala's Forge" README.md; then
    echo -e "${GREEN}✓${NC}"
    ((CHECKS_PASSED++))
else
    echo -e "${RED}✗${NC}"
    ((CHECKS_FAILED++))
fi

# Check web interface features
echo ""
printf "%-50s" "Checking wizard mode in web interface..."
if grep -q "wizard" gui/koalas_forge.html; then
    echo -e "${GREEN}✓${NC}"
    ((CHECKS_PASSED++))
else
    echo -e "${RED}✗${NC}"
    ((CHECKS_FAILED++))
fi

printf "%-50s" "Checking dry run mode implemented..."
if grep -q "dryRunToggle" gui/koalas_forge.html; then
    echo -e "${GREEN}✓${NC}"
    ((CHECKS_PASSED++))
else
    echo -e "${RED}✗${NC}"
    ((CHECKS_FAILED++))
fi

# Git repository
echo ""
printf "%-50s" "Checking git repository initialized..."
if test -d .git; then
    echo -e "${GREEN}✓${NC}"
    ((CHECKS_PASSED++))

    # Check remote
    printf "%-50s" "Checking git remote configured..."
    if git remote -v | grep -q "koalas-forge"; then
        echo -e "${GREEN}✓${NC}"
        ((CHECKS_PASSED++))
    else
        echo -e "${YELLOW}⚠${NC}"
    fi
else
    echo -e "${RED}✗${NC}"
    ((CHECKS_FAILED++))
fi

# Summary
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "Results: ${GREEN}$CHECKS_PASSED passed${NC}, ${RED}$CHECKS_FAILED failed${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

if [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All checks passed! Koala's Forge is ready to use!${NC}"
    echo ""
    echo -e "${BLUE}Quick Start:${NC}"
    echo "  ./launch.sh"
    echo ""
    echo -e "${BLUE}Documentation:${NC}"
    echo "  README.md      - Full documentation"
    echo "  QUICKSTART.md  - Get started in 2 minutes"
    echo ""
    exit 0
else
    echo -e "${RED}⚠️  Some checks failed. Please review and fix issues.${NC}"
    echo ""
    echo -e "${BLUE}Common fixes:${NC}"
    echo "  - Install missing dependencies: pip3 install aiohttp websockets pyyaml"
    echo "  - Make scripts executable: chmod +x launch.sh gui/*.py"
    echo "  - Create missing directories: mkdir -p logs configs demo tests"
    echo ""
    exit 1
fi
