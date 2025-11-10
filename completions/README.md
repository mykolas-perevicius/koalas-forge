# Shell Completions for Koala's Forge

Tab completion support for bash and zsh shells.

## Installation

### Bash

**Option 1: Per-session (temporary)**
```bash
source completions/koala.bash
```

**Option 2: Permanent (add to ~/.bashrc or ~/.bash_profile)**
```bash
echo "source $(pwd)/completions/koala.bash" >> ~/.bashrc
source ~/.bashrc
```

**Option 3: System-wide (requires sudo)**
```bash
sudo cp completions/koala.bash /etc/bash_completion.d/koala
```

### Zsh

**Option 1: User-level**
```bash
# Create completions directory if it doesn't exist
mkdir -p ~/.zsh/completions

# Copy the completion script
cp completions/_koala ~/.zsh/completions/

# Add to ~/.zshrc (if not already present)
echo 'fpath=(~/.zsh/completions $fpath)' >> ~/.zshrc
echo 'autoload -Uz compinit && compinit' >> ~/.zshrc

# Reload
source ~/.zshrc
```

**Option 2: System-wide (requires sudo)**
```bash
sudo cp completions/_koala /usr/local/share/zsh/site-functions/
```

## Features

Once installed, you can use tab completion for:

### Commands
```bash
./koala <TAB>          # Shows all available commands
./koala i<TAB>         # Completes to 'install'
./koala st<TAB>        # Completes to 'status'
```

### Categories
```bash
./koala list --category <TAB>      # Shows all categories
./koala list --category ai<TAB>    # Completes to 'ai_local'
```

### Presets
```bash
./koala preset <TAB>               # Shows available presets
./koala preset ai<TAB>             # Completes to 'ai-developer'
```

### Config Keys
```bash
./koala config get <TAB>           # Shows available config keys
./koala config set <TAB>           # Shows available config keys
```

### Subcommands
```bash
./koala rollback <TAB>             # Shows: list, create, restore
./koala plugin <TAB>               # Shows: list, load, reload
./koala sync <TAB>                 # Shows: status, push, pull
./koala config <TAB>               # Shows: show, get, set, init
```

### Flags
```bash
./koala install <TAB>              # Shows: -y, --dry-run, -s, --sequential, -f, --force
./koala cleanup <TAB>              # Shows: --keep, --dry-run
./koala doctor <TAB>               # Shows: --fix
./koala export --format <TAB>     # Shows: txt, json, yaml
```

### Files
```bash
./koala batch <TAB>                # Completes file names
./koala import <TAB>               # Completes file names
./koala compare <TAB>              # Completes file names
```

## Testing

After installation, test the completion:

```bash
# Test command completion
./koala ins<TAB>         # Should complete to 'install'

# Test flag completion
./koala install --<TAB>  # Should show available flags

# Test category completion
./koala list --category <TAB>  # Should show categories
```

## Troubleshooting

### Bash: Completion not working
1. Make sure bash-completion is installed:
   ```bash
   # macOS
   brew install bash-completion

   # Ubuntu/Debian
   sudo apt-get install bash-completion
   ```

2. Ensure it's loaded in your shell:
   ```bash
   # Add to ~/.bashrc if not present
   if [ -f /etc/bash_completion ]; then
       . /etc/bash_completion
   fi
   ```

### Zsh: Completion not working
1. Make sure compinit is called in your ~/.zshrc:
   ```bash
   autoload -Uz compinit && compinit
   ```

2. Rebuild completion cache:
   ```bash
   rm -f ~/.zcompdump
   compinit
   ```

3. Check your fpath:
   ```bash
   echo $fpath
   ```
   The directory containing `_koala` should be in this list.

## Uninstallation

### Bash
```bash
# If using system-wide installation
sudo rm /etc/bash_completion.d/koala

# If added to ~/.bashrc, remove the source line
# Then reload: source ~/.bashrc
```

### Zsh
```bash
# Remove the completion file
rm ~/.zsh/completions/_koala

# Or for system-wide
sudo rm /usr/local/share/zsh/site-functions/_koala

# Rebuild cache
rm -f ~/.zcompdump && compinit
```
