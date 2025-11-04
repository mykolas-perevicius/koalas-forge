# Contributing to Koala's Forge 🐨

Thank you for your interest in contributing! Koala's Forge is a community project and we welcome contributions of all kinds.

## Ways to Contribute

### 1. Add New Applications

The easiest way to contribute! To add a new app:

1. Edit `apps.yaml`
2. Add your app under the appropriate category
3. Follow this format:

```yaml
- name: "Your App Name"
  package: "package-name"  # Homebrew formula/cask name
  platforms: [mac, linux, windows]
  install_type: "brew"  # or "cask"
  notes: "Brief description"
  priority: medium  # optional: low, medium, high
  post_install: |  # optional
    # Commands to run after installation
```

4. Test your addition
5. Submit a pull request!

### 2. Create New Preset Packs

Add new preset combinations in `koalas_forge.html`:

```javascript
const presets = {
    'your-preset-id': ['app1', 'app2', 'app3'],
};
```

Then add the UI card in the preset grid section.

### 3. Improve the UI

The web interface is in `gui/koalas_forge.html`. Feel free to:
- Enhance the design
- Add new features
- Improve accessibility
- Fix responsive layout issues

### 4. Platform Support

Help us expand to more platforms:
- Add Linux package manager support
- Improve Windows compatibility
- Test on different OS versions

### 5. Bug Fixes

Found a bug? Please:
1. Check if it's already reported in Issues
2. If not, create a detailed bug report
3. Even better - submit a fix!

## Development Setup

```bash
# Clone the repository
git clone https://github.com/mykolas-perevicius/koalas-forge.git
cd koalas-forge

# Install dependencies
pip3 install aiohttp websockets pyyaml

# Run in development mode
./launch.sh
```

## Code Style

- **Python**: Follow PEP 8
- **JavaScript**: Use ES6+ features
- **HTML/CSS**: Keep it clean and readable
- **Comments**: Document complex logic

## Testing

Before submitting:

1. Test your changes on your platform
2. Ensure the web interface loads correctly
3. Test installation/uninstallation if applicable
4. Check for console errors

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to your branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### PR Guidelines

- Provide a clear description of changes
- Reference any related issues
- Include screenshots for UI changes
- Keep changes focused (one feature per PR)

## Adding New Package Managers

To support a new package manager:

1. Update `koalas_forge_server.py` - add detection logic
2. Update `install_single_app()` method
3. Test thoroughly on target platform
4. Document in README.md

## Ideas for Contributions

Not sure where to start? Here are some ideas:

- [ ] Add Windows package manager support (winget, chocolatey)
- [ ] Add Linux package managers (apt, dnf, pacman)
- [ ] Implement app version checking and selective updates
- [ ] Add app dependency visualization
- [ ] Create mobile-responsive improvements
- [ ] Add dark mode toggle
- [ ] Implement installation history/rollback
- [ ] Add app recommendations based on installed apps
- [ ] Create automated tests
- [ ] Improve error handling and user feedback
- [ ] Add internationalization (i18n)
- [ ] Create video tutorials
- [ ] Write installation guides for specific use cases

## Community

- **Issues**: Use GitHub Issues for bugs and feature requests
- **Discussions**: Share ideas and get help
- **Be Respectful**: Follow our code of conduct

## Code of Conduct

- Be kind and respectful
- Welcome newcomers
- Focus on constructive feedback
- Respect different viewpoints and experiences

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

Feel free to open an issue or start a discussion if you have questions!

---

**Thank you for making Koala's Forge better!** 🐨💚
