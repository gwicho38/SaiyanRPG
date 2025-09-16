# SaiyanQuest - Comprehensive Makefile
# Organizes all installation, bootstrapping, and development scripts

# Default target
.PHONY: default
default: help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

# Project variables
PROJECT_NAME := saiyanquest
PYTHON := python3
PIP := pip3
VENV_DIR := .venv
PYTHON_VERSION := 3.11

# Detect OS
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
    OS := linux
endif
ifeq ($(UNAME_S),Darwin)
    OS := macos
endif
ifeq ($(OS),Windows_NT)
    OS := windows
endif

# Help target
.PHONY: help
help:
	@echo "$(BLUE)SaiyanQuest - Development Makefile$(NC)"
	@echo ""
	@echo "$(GREEN)Installation & Setup:$(NC)"
	@echo "  setup          - Complete project setup (recommended for first time)"
	@echo "  install-deps    - Install Python dependencies"
	@echo "  install-dev     - Install development dependencies"
	@echo "  create-venv     - Create virtual environment"
	@echo "  activate-venv   - Show how to activate virtual environment"
	@echo ""
	@echo "$(GREEN)Running the Game:$(NC)"
	@echo "  run             - Run main SaiyanQuest game"
	@echo "  run-systems     - Run game systems launcher"
	@echo "  run-character    - Run character system test"
	@echo "  run-vehicle     - Run vehicle system test"
	@echo "  run-map         - Run map streaming test"
	@echo "  run-effects     - Run vehicle effects test"
	@echo ""
	@echo "$(GREEN)Development:$(NC)"
	@echo "  test            - Run all tests"
	@echo "  test-quick      - Run quick tests"
	@echo "  lint            - Run linting (flake8, pylint)"
	@echo "  format          - Format code (black, isort)"
	@echo "  type-check      - Run type checking (mypy)"
	@echo "  validate        - Validate JSON schemas and data"
	@echo ""
	@echo "$(GREEN)Building & Packaging:$(NC)"
	@echo "  build           - Build the project"
	@echo "  build-android   - Build Android APK"
	@echo "  build-deb       - Build Debian package"
	@echo "  build-flatpak   - Build Flatpak package"
	@echo "  build-windows   - Build Windows installer"
	@echo "  build-portable  - Build portable executables"
	@echo ""
	@echo "$(GREEN)Utilities:$(NC)"
	@echo "  clean           - Clean build artifacts"
	@echo "  clean-all       - Clean everything including cache"
	@echo "  assets          - Download/update game assets"
	@echo "  docs            - Generate documentation"
	@echo "  check-deps      - Check dependency status"
	@echo ""

# =============================================================================
# Installation & Setup
# =============================================================================

.PHONY: setup
setup: create-venv install-deps install-dev
	@echo "$(GREEN)✅ SaiyanQuest setup complete!$(NC)"
	@echo "$(YELLOW)Run 'make activate-venv' to see how to activate the virtual environment$(NC)"

.PHONY: create-venv
create-venv:
	@echo "$(BLUE)Creating virtual environment...$(NC)"
	@$(PYTHON) -m venv $(VENV_DIR)
	@echo "$(GREEN)✅ Virtual environment created in $(VENV_DIR)/$(NC)"

.PHONY: activate-venv
activate-venv:
	@echo "$(YELLOW)To activate the virtual environment, run:$(NC)"
	@echo "$(BLUE)  source $(VENV_DIR)/bin/activate$(NC)"
	@echo "$(YELLOW)Or on Windows:$(NC)"
	@echo "$(BLUE)  $(VENV_DIR)\\Scripts\\activate$(NC)"

.PHONY: install-deps
install-deps:
	@echo "$(BLUE)Installing Python dependencies...$(NC)"
	@$(PIP) install --upgrade pip
	@$(PIP) install -e .
	@echo "$(GREEN)✅ Dependencies installed$(NC)"

.PHONY: install-dev
install-dev:
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	@$(PIP) install tox black isort flake8 mypy pylint
	@echo "$(GREEN)✅ Development dependencies installed$(NC)"

# =============================================================================
# Running the Game
# =============================================================================

.PHONY: run
run:
	@echo "$(BLUE)Running main SaiyanQuest game...$(NC)"
	@$(PYTHON) run_tuxemon.py

.PHONY: run-systems
run-systems:
	@echo "$(BLUE)Running game systems launcher...$(NC)"
	@$(PYTHON) run_game_systems.py

.PHONY: run-character
run-character:
	@echo "$(BLUE)Running character system test...$(NC)"
	@$(PYTHON) test_character_system.py

.PHONY: run-vehicle
run-vehicle:
	@echo "$(BLUE)Running vehicle system test...$(NC)"
	@$(PYTHON) test_vehicle_systems.py

.PHONY: run-map
run-map:
	@echo "$(BLUE)Running map streaming test...$(NC)"
	@$(PYTHON) test_map_data_streaming.py

.PHONY: run-effects
run-effects:
	@echo "$(BLUE)Running vehicle effects test...$(NC)"
	@$(PYTHON) test_vehicle_effects.py

.PHONY: run-world-3d
run-world-3d:
	@echo "$(BLUE)Running 3D world system test...$(NC)"
	@$(PYTHON) test_world_3d_system.py

.PHONY: run-physics
run-physics:
	@echo "$(BLUE)Running physics system test...$(NC)"
	@$(PYTHON) test_physics_system.py

# =============================================================================
# Development & Testing
# =============================================================================

.PHONY: test
test:
	@echo "$(BLUE)Running all tests...$(NC)"
	@tox -e py3

.PHONY: test-quick
test-quick:
	@echo "$(BLUE)Running quick tests...$(NC)"
	@$(PYTHON) -m pytest tests/ -v --tb=short

.PHONY: test-systems
test-systems:
	@echo "$(BLUE)Testing all game systems...$(NC)"
	@$(PYTHON) test_character_system.py &
	@$(PYTHON) test_vehicle_systems.py &
	@$(PYTHON) test_map_data_streaming.py &
	@$(PYTHON) test_vehicle_effects.py &
	@wait

.PHONY: lint
lint:
	@echo "$(BLUE)Running linting...$(NC)"
	@flake8 saiyanquest/ tests/
	@pylint saiyanquest/

.PHONY: format
format:
	@echo "$(BLUE)Formatting code...$(NC)"
	@black saiyanquest/ tests/
	@isort saiyanquest/ tests/

.PHONY: type-check
type-check:
	@echo "$(BLUE)Running type checking...$(NC)"
	@mypy saiyanquest/

.PHONY: validate
validate:
	@echo "$(BLUE)Validating JSON schemas and data...$(NC)"
	@PYTHONPATH=. $(PYTHON) scripts/schema.py --validate
	@PYTHONPATH=. $(PYTHON) scripts/test_actions.py

# =============================================================================
# Building & Packaging
# =============================================================================

.PHONY: build
build:
	@echo "$(BLUE)Building SaiyanQuest...$(NC)"
	@$(PYTHON) -m build

.PHONY: build-android
build-android:
	@echo "$(BLUE)Building Android APK...$(NC)"
	@chmod +x buildconfig/build_android.sh
	@./buildconfig/build_android.sh

.PHONY: build-deb
build-deb:
	@echo "$(BLUE)Building Debian package...$(NC)"
	@chmod +x buildconfig/build_deb.sh
	@./buildconfig/build_deb.sh

.PHONY: build-flatpak
build-flatpak:
	@echo "$(BLUE)Building Flatpak package...$(NC)"
	@chmod +x buildconfig/build_flatpak.sh
	@./buildconfig/build_flatpak.sh

.PHONY: build-windows
build-windows:
	@echo "$(BLUE)Building Windows installer...$(NC)"
	@chmod +x buildconfig/build_installer.sh
	@./buildconfig/build_installer.sh

.PHONY: build-portable
build-portable:
	@echo "$(BLUE)Building portable executables...$(NC)"
	@chmod +x buildconfig/build_pypy_portable_linux.sh
	@chmod +x buildconfig/build_pypy_portable_windows.sh
	@./buildconfig/build_pypy_portable_linux.sh
	@./buildconfig/build_pypy_portable_windows.sh

.PHONY: build-opk
build-opk:
	@echo "$(BLUE)Building OpenDingux OPK...$(NC)"
	@chmod +x buildconfig/build_opk.sh
	@./buildconfig/build_opk.sh

# =============================================================================
# Utilities
# =============================================================================

.PHONY: clean
clean:
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	@rm -rf build/
	@rm -rf dist/
	@rm -rf *.egg-info/
	@rm -rf __pycache__/
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@echo "$(GREEN)✅ Build artifacts cleaned$(NC)"

.PHONY: clean-all
clean-all: clean
	@echo "$(BLUE)Cleaning everything...$(NC)"
	@rm -rf $(VENV_DIR)/
	@rm -rf .tox/
	@rm -rf .pytest_cache/
	@rm -rf .mypy_cache/
	@rm -rf .coverage
	@rm -rf htmlcov/
	@echo "$(GREEN)✅ Everything cleaned$(NC)"

.PHONY: assets
assets:
	@echo "$(BLUE)Downloading/updating game assets...$(NC)"
	@$(PYTHON) scripts/download_technique_animations.py
	@echo "$(GREEN)✅ Assets updated$(NC)"

.PHONY: docs
docs:
	@echo "$(BLUE)Generating documentation...$(NC)"
	@$(PYTHON) -m pydoc -w saiyanquest
	@echo "$(GREEN)✅ Documentation generated$(NC)"

.PHONY: check-deps
check-deps:
	@echo "$(BLUE)Checking dependency status...$(NC)"
	@$(PYTHON) scripts/test_deps.py
	@echo "$(GREEN)✅ Dependencies checked$(NC)"

.PHONY: check-sprites
check-sprites:
	@echo "$(BLUE)Checking sprite files...$(NC)"
	@$(PYTHON) scripts/check_sprites.py
	@echo "$(GREEN)✅ Sprites checked$(NC)"

.PHONY: optimize-images
optimize-images:
	@echo "$(BLUE)Optimizing images...$(NC)"
	@chmod +x scripts/image_optim_optipng.sh
	@chmod +x scripts/image_optim_oxipng.sh
	@./scripts/image_optim_optipng.sh
	@./scripts/image_optim_oxipng.sh
	@echo "$(GREEN)✅ Images optimized$(NC)"

# =============================================================================
# Development Tools
# =============================================================================

.PHONY: debug-menu
debug-menu:
	@echo "$(BLUE)Running menu debug...$(NC)"
	@$(PYTHON) test_menu_debug.py

.PHONY: debug-ui
debug-ui:
	@echo "$(BLUE)Running UI debug...$(NC)"
	@$(PYTHON) test_ui_debug.py

.PHONY: debug-physics
debug-physics:
	@echo "$(BLUE)Running physics debug...$(NC)"
	@$(PYTHON) test_physics_system.py

.PHONY: debug-vehicles
debug-vehicles:
	@echo "$(BLUE)Running vehicle debug...$(NC)"
	@$(PYTHON) test_vehicle_issue2.py

.PHONY: debug-characters
debug-characters:
	@echo "$(BLUE)Running character debug...$(NC)"
	@$(PYTHON) test_character_issue3.py

# =============================================================================
# Platform-specific targets
# =============================================================================

.PHONY: setup-wine
setup-wine:
	@echo "$(BLUE)Setting up Wine environment...$(NC)"
	@chmod +x buildconfig/setup_wine_debian10.sh
	@chmod +x buildconfig/setup_wine_ubuntu_focal.sh
	@if [ -f /etc/debian_version ]; then \
		./buildconfig/setup_wine_debian10.sh; \
	else \
		./buildconfig/setup_wine_ubuntu_focal.sh; \
	fi

.PHONY: setup-cx-freeze
setup-cx-freeze:
	@echo "$(BLUE)Setting up cx_Freeze...$(NC)"
	@$(PYTHON) buildconfig/setup_cx_freeze.py

# =============================================================================
# Maintenance
# =============================================================================

.PHONY: update-deps
update-deps:
	@echo "$(BLUE)Updating dependencies...$(NC)"
	@$(PIP) install --upgrade -e .
	@echo "$(GREEN)✅ Dependencies updated$(NC)"

.PHONY: freeze-deps
freeze-deps:
	@echo "$(BLUE)Freezing dependencies...$(NC)"
	@$(PIP) freeze > requirements-frozen.txt
	@echo "$(GREEN)✅ Dependencies frozen to requirements-frozen.txt$(NC)"

.PHONY: audit-textures
audit-textures:
	@echo "$(BLUE)Auditing missing textures...$(NC)"
	@$(PYTHON) audit_missing_textures.py
	@echo "$(GREEN)✅ Texture audit complete$(NC)"

.PHONY: sync-wiki
sync-wiki:
	@echo "$(BLUE)Syncing with wiki monsters...$(NC)"
	@$(PYTHON) scripts/sync-wiki-monsters.py
	@echo "$(GREEN)✅ Wiki sync complete$(NC)"

# =============================================================================
# Quick development workflow
# =============================================================================

.PHONY: dev-setup
dev-setup: setup
	@echo "$(GREEN)✅ Development environment ready!$(NC)"
	@echo "$(YELLOW)Quick commands:$(NC)"
	@echo "  make run-systems    - Launch game systems"
	@echo "  make test-quick     - Run quick tests"
	@echo "  make format         - Format code"
	@echo "  make lint           - Check code quality"

.PHONY: quick-test
quick-test: format lint test-quick
	@echo "$(GREEN)✅ Quick development cycle complete!$(NC)"

.PHONY: full-test
full-test: format lint type-check test validate
	@echo "$(GREEN)✅ Full test suite complete!$(NC)"

# =============================================================================
# Special targets
# =============================================================================

.PHONY: install-system
install-system:
	@echo "$(BLUE)Installing SaiyanQuest system-wide...$(NC)"
	@sudo $(PIP) install -e .
	@echo "$(GREEN)✅ SaiyanQuest installed system-wide$(NC)"

.PHONY: uninstall
uninstall:
	@echo "$(BLUE)Uninstalling SaiyanQuest...$(NC)"
	@$(PIP) uninstall $(PROJECT_NAME) -y
	@echo "$(GREEN)✅ SaiyanQuest uninstalled$(NC)"

.PHONY: reinstall
reinstall: uninstall install-deps
	@echo "$(GREEN)✅ SaiyanQuest reinstalled$(NC)"

# =============================================================================
# Information targets
# =============================================================================

.PHONY: info
info:
	@echo "$(BLUE)SaiyanQuest Project Information$(NC)"
	@echo "Project: $(PROJECT_NAME)"
	@echo "Python: $(PYTHON)"
	@echo "OS: $(OS)"
	@echo "Virtual Env: $(VENV_DIR)"
	@echo ""
	@echo "$(YELLOW)Available targets:$(NC)"
	@echo "  make help         - Show this help"
	@echo "  make setup        - Complete setup"
	@echo "  make run-systems  - Run game systems"
	@echo "  make test         - Run tests"
	@echo "  make build        - Build project"

.PHONY: version
version:
	@$(PYTHON) -c "import saiyanquest; print(saiyanquest.__version__)" 2>/dev/null || echo "Version not available"

# =============================================================================
# Legacy compatibility
# =============================================================================

# Keep original targets for backward compatibility
.PHONY: validate-legacy
validate-legacy: validate

.PHONY: run-legacy
run-legacy: run

# =============================================================================
# End of Makefile
# =============================================================================