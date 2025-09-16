#!/bin/bash
# SaiyanQuest - Shell Script Alternative to Makefile
# Provides the same functionality as the Makefile for users who prefer shell scripts

set -e  # Exit on any error

# Colors for output
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Project variables
PROJECT_NAME="saiyanquest"
PYTHON="python3"
PIP="pip3"
VENV_DIR=".venv"

# Function to print colored output
print_color() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to show help
show_help() {
    print_color $BLUE "SaiyanQuest - Shell Script Commands"
    echo ""
    print_color $GREEN "Installation & Setup:"
    echo "  ./saiyanquest.sh setup          - Complete project setup"
    echo "  ./saiyanquest.sh install-deps   - Install Python dependencies"
    echo "  ./saiyanquest.sh create-venv    - Create virtual environment"
    echo ""
    print_color $GREEN "Running the Game:"
    echo "  ./saiyanquest.sh run            - Run main SaiyanQuest game"
    echo "  ./saiyanquest.sh run-systems    - Run game systems launcher"
    echo "  ./saiyanquest.sh run-character  - Run character system test"
    echo "  ./saiyanquest.sh run-vehicle    - Run vehicle system test"
    echo "  ./saiyanquest.sh run-map        - Run map streaming test"
    echo "  ./saiyanquest.sh run-effects    - Run vehicle effects test"
    echo ""
    print_color $GREEN "Development:"
    echo "  ./saiyanquest.sh test           - Run all tests"
    echo "  ./saiyanquest.sh lint           - Run linting"
    echo "  ./saiyanquest.sh format         - Format code"
    echo "  ./saiyanquest.sh validate       - Validate JSON schemas"
    echo ""
    print_color $GREEN "Utilities:"
    echo "  ./saiyanquest.sh clean          - Clean build artifacts"
    echo "  ./saiyanquest.sh clean-all      - Clean everything"
    echo "  ./saiyanquest.sh check-deps     - Check dependencies"
    echo ""
}

# Function to create virtual environment
create_venv() {
    print_color $BLUE "Creating virtual environment..."
    $PYTHON -m venv $VENV_DIR
    print_color $GREEN "✅ Virtual environment created in $VENV_DIR/"
}

# Function to install dependencies
install_deps() {
    print_color $BLUE "Installing Python dependencies..."
    $PIP install --upgrade pip
    $PIP install -e .
    print_color $GREEN "✅ Dependencies installed"
}

# Function to install development dependencies
install_dev() {
    print_color $BLUE "Installing development dependencies..."
    $PIP install tox black isort flake8 mypy pylint
    print_color $GREEN "✅ Development dependencies installed"
}

# Function to run the game systems launcher
run_systems() {
    print_color $BLUE "Running game systems launcher..."
    $PYTHON run_game_systems.py
}

# Function to run character system test
run_character() {
    print_color $BLUE "Running character system test..."
    $PYTHON test_character_system.py
}

# Function to run vehicle system test
run_vehicle() {
    print_color $BLUE "Running vehicle system test..."
    $PYTHON test_vehicle_systems.py
}

# Function to run map streaming test
run_map() {
    print_color $BLUE "Running map streaming test..."
    $PYTHON test_map_data_streaming.py
}

# Function to run vehicle effects test
run_effects() {
    print_color $BLUE "Running vehicle effects test..."
    $PYTHON test_vehicle_effects.py
}

# Function to run tests
run_tests() {
    print_color $BLUE "Running all tests..."
    tox -e py3
}

# Function to run linting
run_lint() {
    print_color $BLUE "Running linting..."
    flake8 saiyanquest/ tests/
    pylint saiyanquest/
}

# Function to format code
format_code() {
    print_color $BLUE "Formatting code..."
    black saiyanquest/ tests/
    isort saiyanquest/ tests/
}

# Function to validate schemas
validate_schemas() {
    print_color $BLUE "Validating JSON schemas and data..."
    PYTHONPATH=. $PYTHON scripts/schema.py --validate
    PYTHONPATH=. $PYTHON scripts/test_actions.py
}

# Function to clean build artifacts
clean_build() {
    print_color $BLUE "Cleaning build artifacts..."
    rm -rf build/ dist/ *.egg-info/ __pycache__/
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete
    print_color $GREEN "✅ Build artifacts cleaned"
}

# Function to clean everything
clean_all() {
    clean_build
    print_color $BLUE "Cleaning everything..."
    rm -rf $VENV_DIR/ .tox/ .pytest_cache/ .mypy_cache/ .coverage htmlcov/
    print_color $GREEN "✅ Everything cleaned"
}

# Function to check dependencies
check_deps() {
    print_color $BLUE "Checking dependency status..."
    $PYTHON scripts/test_deps.py
    print_color $GREEN "✅ Dependencies checked"
}

# Function to show project info
show_info() {
    print_color $BLUE "SaiyanQuest Project Information"
    echo "Project: $PROJECT_NAME"
    echo "Python: $PYTHON"
    echo "OS: $(uname -s)"
    echo "Virtual Env: $VENV_DIR"
    echo ""
    print_color $YELLOW "Available commands:"
    echo "  ./saiyanquest.sh help         - Show this help"
    echo "  ./saiyanquest.sh setup        - Complete setup"
    echo "  ./saiyanquest.sh run-systems  - Run game systems"
    echo "  ./saiyanquest.sh test         - Run tests"
}

# Main command dispatcher
case "${1:-help}" in
    "help"|"--help"|"-h")
        show_help
        ;;
    "setup")
        create_venv
        install_deps
        install_dev
        print_color $GREEN "✅ SaiyanQuest setup complete!"
        print_color $YELLOW "Run 'source $VENV_DIR/bin/activate' to activate the virtual environment"
        ;;
    "create-venv")
        create_venv
        ;;
    "install-deps")
        install_deps
        ;;
    "install-dev")
        install_dev
        ;;
    "run")
        $PYTHON run_tuxemon.py
        ;;
    "run-systems")
        run_systems
        ;;
    "run-character")
        run_character
        ;;
    "run-vehicle")
        run_vehicle
        ;;
    "run-map")
        run_map
        ;;
    "run-effects")
        run_effects
        ;;
    "test")
        run_tests
        ;;
    "lint")
        run_lint
        ;;
    "format")
        format_code
        ;;
    "validate")
        validate_schemas
        ;;
    "clean")
        clean_build
        ;;
    "clean-all")
        clean_all
        ;;
    "check-deps")
        check_deps
        ;;
    "info")
        show_info
        ;;
    *)
        print_color $RED "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac