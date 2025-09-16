# SaiyanQuest Development Setup

This document explains the comprehensive development setup for SaiyanQuest, including all installation and bootstrapping scripts organized into easy-to-use commands.

## 🚀 Quick Start

### Option 1: Using Makefile (Recommended)
```bash
# First-time setup
make setup

# Run the game systems launcher
make run-systems
```

### Option 2: Using Shell Script
```bash
# First-time setup
./saiyanquest.sh setup

# Run the game systems launcher
./saiyanquest.sh run-systems
```

## 📁 Project Organization

The SaiyanQuest project is now organized with comprehensive build and development tools:

### Core Files
- **`Makefile`** - Comprehensive build system with 50+ commands
- **`saiyanquest.sh`** - Shell script alternative to Makefile
- **`MAKEFILE_README.md`** - Detailed documentation for all Makefile commands
- **`pyproject.toml`** - Modern Python project configuration
- **`requirements.txt.backup`** - Legacy requirements (backup)

### Build Configuration
- **`buildconfig/`** - Platform-specific build scripts
  - `build_android.sh` - Android APK build
  - `build_deb.sh` - Debian package build
  - `build_flatpak.sh` - Flatpak package build
  - `build_installer.sh` - Windows installer build
  - `build_pypy_portable_*.sh` - Portable executable builds

### Development Scripts
- **`scripts/`** - Development and maintenance scripts
  - `schema.py` - JSON schema validation
  - `test_actions.py` - Action testing
  - `check_sprites.py` - Sprite validation
  - `download_technique_animations.py` - Asset downloading
  - Various optimization and maintenance scripts

### Test Files
- **`test_*.py`** - Individual system tests
  - `test_character_system.py` - Character system test
  - `test_vehicle_systems.py` - Vehicle system test
  - `test_map_data_streaming.py` - Map streaming test
  - `test_vehicle_effects.py` - Vehicle effects test
  - `test_world_3d_system.py` - 3D world system test
  - `test_physics_system.py` - Physics system test

## 🛠️ Available Commands

### Installation & Setup
```bash
make setup              # Complete project setup
make install-deps       # Install Python dependencies
make install-dev         # Install development dependencies
make create-venv         # Create virtual environment
make activate-venv       # Show activation instructions
```

### Running the Game
```bash
make run                # Run main SaiyanQuest game
make run-systems        # Run game systems launcher
make run-character      # Run character system test
make run-vehicle        # Run vehicle system test
make run-map           # Run map streaming test
make run-effects       # Run vehicle effects test
make run-world-3d      # Run 3D world system test
make run-physics       # Run physics system test
```

### Development & Testing
```bash
make test              # Run all tests
make test-quick        # Run quick tests
make test-systems      # Test all game systems
make lint              # Run linting (flake8, pylint)
make format            # Format code (black, isort)
make type-check         # Run type checking (mypy)
make validate          # Validate JSON schemas and data
```

### Building & Packaging
```bash
make build             # Build the project
make build-android     # Build Android APK
make build-deb         # Build Debian package
make build-flatpak     # Build Flatpak package
make build-windows     # Build Windows installer
make build-portable    # Build portable executables
make build-opk         # Build OpenDingux OPK
```

### Utilities
```bash
make clean             # Clean build artifacts
make clean-all         # Clean everything including cache
make assets            # Download/update game assets
make docs              # Generate documentation
make check-deps         # Check dependency status
make check-sprites      # Check sprite files
make optimize-images   # Optimize images
```

### Development Tools
```bash
make debug-menu        # Run menu debug
make debug-ui          # Run UI debug
make debug-physics     # Run physics debug
make debug-vehicles    # Run vehicle debug
make debug-characters  # Run character debug
```

### Quick Development Workflow
```bash
make dev-setup         # Complete development environment setup
make quick-test         # Quick development cycle (format + lint + test)
make full-test         # Full test suite (format + lint + type-check + test + validate)
```

## 🔧 Development Workflow

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

## 🎮 Game Systems

The SaiyanQuest project includes multiple game systems that can be tested individually:

1. **Character System** (`make run-character`)
   - Interactive characters with AI personalities
   - Physics, ragdoll effects, conversations
   - Controls: WASD, E to interact

2. **Vehicle System** (`make run-vehicle`)
   - Advanced vehicle physics and controls
   - Electrical/mechanical systems
   - Multiple vehicle types

3. **Map Streaming System** (`make run-map`)
   - Large world chunk loading/unloading
   - Memory management and LOD system
   - Performance monitoring

4. **Vehicle Effects System** (`make run-effects`)
   - Particle systems and visual effects
   - Tire smoke, engine exhaust, brake effects

5. **3D World System** (`make run-world-3d`)
   - Multi-layered 3D world rendering
   - Camera controls (WASD + Q/E)
   - Dynamic object management

6. **Physics System** (`make run-physics`)
   - Box2D physics integration
   - Collision detection and response
   - Realistic vehicle physics

## 🐛 Debugging

Individual system debugging:
```bash
make debug-menu        # Debug menu system
make debug-ui          # Debug UI components
make debug-physics     # Debug physics system
make debug-vehicles    # Debug vehicle issues
make debug-characters  # Debug character issues
```

## 📦 Dependencies

The project uses modern Python packaging with `pyproject.toml`:

### Core Dependencies
- `pygame-ce==2.5.3` - Game engine
- `box2d>=2.3.10` - Physics engine
- `pytmx==3.32` - TMX map loading
- `pyscroll>=2.31` - Map scrolling
- `pillow` - Image processing
- `pygame-menu-ce==4.5.2` - Menu system

### Development Dependencies
- `tox` - Testing framework
- `black` - Code formatting
- `isort` - Import sorting
- `flake8` - Linting
- `mypy` - Type checking
- `pylint` - Advanced linting

## 🔍 Troubleshooting

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

## 🌍 Platform Support

- **Linux**: Full support for all commands
- **macOS**: Full support for all commands  
- **Windows**: Most commands supported (some shell scripts may need WSL)

## 📚 Additional Resources

- **`MAKEFILE_README.md`** - Detailed Makefile documentation
- **`CONTRIBUTING.md`** - Contribution guidelines
- **`README.md`** - Project overview
- **`docs/`** - Additional documentation

## 🎯 Next Steps

1. **Run the setup**: `make setup`
2. **Test the systems**: `make run-systems`
3. **Start developing**: `make quick-test`
4. **Read the docs**: Check `MAKEFILE_README.md` for detailed command reference

The SaiyanQuest development environment is now fully organized and ready for productive development! 🚀