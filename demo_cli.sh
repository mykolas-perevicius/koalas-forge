#!/bin/bash
# 🐨 Koala's Forge CLI Demo
# Demonstrates all CLI features

set -e

echo "🐨 Koala's Forge CLI Demo"
echo "================================"
echo ""

# Check version
echo "📌 Step 1: Check version"
./koala version
echo ""
read -p "Press Enter to continue..."
echo ""

# List categories
echo "📌 Step 2: List all categories"
./koala categories
echo ""
read -p "Press Enter to continue..."
echo ""

# Search for packages
echo "📌 Step 3: Search for packages"
echo "Searching for 'python'..."
./koala search python
echo ""
read -p "Press Enter to continue..."
echo ""

# List packages in a category
echo "📌 Step 4: List packages in Development Core category"
./koala list --category development_core
echo ""
read -p "Press Enter to continue..."
echo ""

# Check system status
echo "📌 Step 5: Check system status"
./koala status
echo ""
read -p "Press Enter to continue..."
echo ""

# List plugins
echo "📌 Step 6: List loaded plugins"
./koala plugin list
echo ""
read -p "Press Enter to continue..."
echo ""

# List rollback snapshots
echo "📌 Step 7: List rollback snapshots"
./koala rollback list
echo ""
read -p "Press Enter to continue..."
echo ""

# Cloud sync status
echo "📌 Step 8: Check cloud sync status"
./koala sync status
echo ""
read -p "Press Enter to continue..."
echo ""

# Dry run installation
echo "📌 Step 9: Dry run installation (simulate)"
echo "Simulating installation of 'git'..."
./koala install git --dry-run
echo ""
read -p "Press Enter to continue..."
echo ""

# Create rollback snapshot
echo "📌 Step 10: Create a rollback snapshot"
./koala rollback create "Demo snapshot - $(date)"
echo ""
read -p "Press Enter to continue..."
echo ""

# List snapshots again
echo "📌 Step 11: View updated snapshots"
./koala rollback list
echo ""
read -p "Press Enter to continue..."
echo ""

# View events
echo "📌 Step 12: View recent events"
./koala events -n 10
echo ""

echo "✨ Demo complete!"
echo ""
echo "Try these commands yourself:"
echo "  ./koala search <query>        - Search for packages"
echo "  ./koala install <app>         - Install an application"
echo "  ./koala install <app> --dry-run - Simulate installation"
echo "  ./koala rollback list         - List snapshots"
echo "  ./koala categories            - List categories"
echo "  ./koala --help                - See all commands"
