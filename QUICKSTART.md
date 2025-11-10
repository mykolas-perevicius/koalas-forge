# 🚀 Koala's Forge - Quick Start

Get up and running with Koala's Forge in 5 minutes!

## Installation

```bash
# Clone the repository
git clone https://github.com/mykolas-perevicius/koalas-forge.git
cd koalas-forge

# Make the CLI executable (one-time setup)
chmod +x koala
```

## 🎯 Most Common Commands

```bash
# Browse what's available
./koala categories                    # List all 14 categories
./koala search python                 # Search for packages
./koala list --category ai_local      # Browse category

# Install packages
./koala install git docker python     # Install tools
./koala install git --dry-run         # Test without installing

# Safety & rollback
./koala rollback create "My snapshot" # Create backup point
./koala rollback list                 # List all snapshots

# System info
./koala status                        # Check system status
./koala version                       # Show version
```

## 📖 Full Documentation

- **Complete CLI Guide:** [CLI_GUIDE.md](CLI_GUIDE.md)
- **Main README:** [README.md](README.md)
- **Interactive Demo:** Run `./demo_cli.sh`

---

**Start exploring:** `./koala categories` 🐨
