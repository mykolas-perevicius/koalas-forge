# Example Package Lists

This directory contains example package lists for common setups. Use them with the `./koala batch` command.

## Available Examples

### dev-setup.txt
Essential development tools for any developer.
```bash
./koala batch examples/dev-setup.txt
```
Includes: git, python, node.js, docker

### ai-researcher.txt
Setup for AI and machine learning research.
```bash
./koala batch examples/ai-researcher.txt
```
Includes: python, ollama, jupyter, git, docker

### full-stack.txt
Complete full-stack development environment.
```bash
./koala batch examples/full-stack.txt
```
Includes: git, docker, python, node.js, go, rust, databases, and tools

## Using Package Lists

### Install from a list
```bash
./koala batch examples/dev-setup.txt
```

### Preview what would be installed (dry-run)
```bash
./koala batch examples/full-stack.txt --dry-run
```

### Create your own list
1. Create a text file with one package name per line
2. Add comments with `#`
3. Install with: `./koala batch mysetup.txt`

Example:
```text
# My Custom Setup
git
docker
python-3.11

# Optional tools
# postman
# kubernetes-cli
```

### Compare your setup
```bash
# See what's different between file and your system
./koala compare examples/dev-setup.txt
```

### Export your current setup
```bash
# Create a package list from your installed packages
./koala export my-setup.txt
```

## Tips

- Use `./koala search <name>` to find exact package names
- Use `./koala categories` to browse available packages
- Use `./koala info <package>` to see details before installing
- Files support comments (`#`) and blank lines
- Package names are case-insensitive and match the names in `./koala list`
