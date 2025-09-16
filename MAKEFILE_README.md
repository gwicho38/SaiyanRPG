# SaiyanQuest Makefile Documentation

This comprehensive Makefile organizes all installation, bootstrapping, and development scripts for the SaiyanQuest project.

## Quick Start

For first-time setup:
```bash
make setup
```

To run the game systems launcher:
```bash
make run-systems
```

## Available Commands

### Installation & Setup

| Command | Description |
|---------|-------------|
| `make setup` | Complete project setup (recommended for first time) |
| `make install-deps` | Install Python dependencies |
| `make install-dev` | Install development dependencies |
| `make create-venv` | Create virtual environment |
| `make activate-venv` | Show how to activate virtual environment |

### Running the Game

| Command | Description |
|---------|-------------|
| `make run` | Run main SaiyanQuest game |
| `make run-systems` | Run game systems launcher |
| `make run-character` | Run character system test |
| `make run-vehicle` | Run vehicle system test |
| `make run-map` | Run map streaming test |
| `make run-effects` | Run vehicle effects test |
| `make run-world-3d` | Run 3D world system test |
| `make run-physics` | Run physics system test |

### Development & Testing

| Command | Description |
|---------|-------------|
| `make test` | Run all tests |
| `make test-quick` | Run quick tests |
| `make test-systems` | Test all game systems |
| `make lint` | Run linting (flake8, pylint) |
| `make format` | Format code (black, isort) |
| `make type-check` | Run type checking (mypy) |
| `make validate` | Validate JSON schemas and data |

### Building & Packaging

| Command | Description |
|---------|-------------|
| `make build` | Build the project |
| `make build-android` | Build Android APK |
| `make build-deb` | Build Debian package |
| `make build-flatpak` | Build Flatpak package |
| `make build-windows` | Build Windows installer |
| `make build-portable` | Build portable executables |
| `make build-opk` | Build OpenDingux OPK |

### Utilities

| Command | Description |
|---------|-------------|
| `make clean` | Clean build artifacts |
| `make clean-all` | Clean everything including cache |
| `make assets` | Download/update game assets |
| `make docs` | Generate documentation |
| `make check-deps` | Check dependency status |
| `make check-sprites` | Check sprite files |
| `make optimize-images` | Optimize images |

### Development Tools

| Command | Description |
|---------|-------------|
| `make debug-menu` | Run menu debug |
| `make debug-ui` | Run UI debug |
| `make debug-physics` | Run physics debug |
| `make debug-vehicles` | Run vehicle debug |
| `make debug-characters` | Run character debug |

### Platform-specific

| Command | Description |
|---------|-------------|
| `make setup-wine` | Set up Wine environment |
| `make setup-cx-freeze` | Set up cx_Freeze |

### Maintenance

| Command | Description |
|---------|-------------|
| `make update-deps` | Update dependencies |
| `make freeze-deps` | Freeze dependencies to file |
| `make audit-textures` | Audit missing textures |
| `make sync-wiki` | Sync with wiki monsters |

### Quick Development Workflow

| Command | Description |
|---------|-------------|
| `make dev-setup` | Complete development environment setup |
| `make quick-test` | Quick development cycle (format + lint + test) |
| `make full-test` | Full test suite (format + lint + type-check + test + validate) |

### Special Commands

| Command | Description |
|---------|-------------|
| `make install-system` | Install SaiyanQuest system-wide |
| `make uninstall` | Uninstall SaiyanQuest |
| `make reinstall` | Reinstall SaiyanQuest |
| `make info` | Show project information |
| `make version` | Show current version |

## Development Workflow Examples

### First Time Setup
```bash
# Clone the repository
git clone https://github.com/SaiyanQuest/SaiyanQuest.git
cd SaiyanQuest

# Complete setup
make setup

# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows

# Run the game systems
make run-systems
```

### Daily Development
```bash
# Quick development cycle
make quick-test

# Run specific system tests
make run-character
make run-vehicle

# Format and check code
make format
make lint
```

### Before Committing
```bash
# Full test suite
make full-test

# Clean up
make clean
```

### Building for Distribution
```bash
# Build for current platform
make build

# Build for specific platforms
make build-android
make build-windows
make build-deb
```

## Environment Variables

The Makefile respects these environment variables:

- `PYTHON`: Python executable (default: `python3`)
- `PIP`: Pip executable (default: `pip3`)
- `VENV_DIR`: Virtual environment directory (default: `.venv`)
- `PYTHON_VERSION`: Python version (default: `3.11`)

## Platform Support

The Makefile automatically detects the operating system and provides platform-specific commands:

- **Linux**: Full support for all commands
- **macOS**: Full support for all commands
- **Windows**: Most commands supported (some shell scripts may need WSL)

## Troubleshooting

### Virtual Environment Issues
```bash
# Recreate virtual environment
make clean-all
make setup
```

### Dependency Issues
```bash
# Update dependencies
make update-deps

# Check dependency status
make check-deps
```

### Build Issues
```bash
# Clean everything and rebuild
make clean-all
make setup
make build
```

### Permission Issues (Linux/macOS)
```bash
# Fix script permissions
chmod +x buildconfig/*.sh
chmod +x scripts/*.sh
```

## Contributing

When adding new functionality:

1. Add new targets to the appropriate section in the Makefile
2. Update this documentation
3. Test on multiple platforms
4. Ensure backward compatibility

## Legacy Compatibility

The Makefile maintains compatibility with the original targets:
- `make validate` → `make validate-legacy`
- `make run` → `make run-legacy`

## Notes

- All commands are designed to be idempotent (safe to run multiple times)
- Commands automatically handle virtual environment activation when needed
- Color-coded output helps identify success/failure states
- Cross-platform compatibility is maintained where possible