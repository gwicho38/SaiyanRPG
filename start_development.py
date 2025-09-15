#!/usr/bin/env python3
"""
Start Development Script for SaiyanQuest GTA
Helps you begin systematic development of features
"""

import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = ['pygame', 'pytmx']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} (missing)")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing_packages, check=True)
            print("✅ Dependencies installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return False
    
    return True

def setup_issue_tracker():
    """Set up the issue tracker"""
    print("\n🎯 Setting up issue tracker...")
    
    try:
        from issue_tracker import IssueTracker, create_default_issues
        
        tracker = IssueTracker()
        
        if not tracker.issues:
            print("   Creating default issues from roadmap...")
            create_default_issues(tracker)
            print("   ✅ Default issues created")
        else:
            print("   ✅ Issue tracker already initialized")
        
        return tracker
    except Exception as e:
        print(f"   ❌ Failed to setup issue tracker: {e}")
        return None

def show_next_steps(tracker):
    """Show next steps for development"""
    if not tracker:
        return
    
    print("\n🚀 Next Steps:")
    print("=" * 40)
    
    # Show current progress
    tracker.show_progress()
    
    # Show next issue
    next_issue = tracker.get_next_issue()
    if next_issue:
        print(f"\n🎯 Recommended Next Issue: #{next_issue.id}")
        print(f"   Title: {next_issue.title}")
        print(f"   Priority: {next_issue.priority.value.upper()}")
        print(f"   Estimated Time: {next_issue.estimated_time}")
        
        print(f"\n📋 To start working on this issue:")
        print(f"   python issue_tracker.py")
        print(f"   > start {next_issue.id} your_name")
    
    # Show available commands
    print(f"\n🛠️ Available Development Tools:")
    print(f"   • Issue Tracker: python issue_tracker.py")
    print(f"   • Pixel Art Test: python test_simple_pixel_art.py")
    print(f"   • Full Pixel Art Test: python test_pixel_art_maps.py")
    print(f"   • Run GTA Game: python saiyanquest/gta_game.py")

def create_development_workspace():
    """Create development workspace structure"""
    print("\n📁 Setting up development workspace...")
    
    workspace_dirs = [
        "development/physics",
        "development/vehicles", 
        "development/ai",
        "development/world",
        "development/traffic",
        "development/audio",
        "development/multiplayer",
        "development/tools",
        "development/tests"
    ]
    
    for dir_path in workspace_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ {dir_path}")
    
    # Create development README
    readme_content = """# SaiyanQuest GTA - Development Workspace

## 🎯 Current Status
- ✅ Pixel Art Map System: COMPLETED
- ⏳ Physics System Upgrade: PENDING
- ⏳ Enhanced Vehicle System: PENDING
- ⏳ Advanced Character AI: PENDING

## 🛠️ Development Tools
- `issue_tracker.py` - Track development progress
- `test_simple_pixel_art.py` - Test pixel art assets
- `test_pixel_art_maps.py` - Test full pixel art system

## 📋 Next Steps
1. Run `python start_development.py` to get started
2. Use `python issue_tracker.py` to manage issues
3. Start with Issue #1: Physics System Upgrade

## 🎮 Testing
- Test pixel art system: `python test_simple_pixel_art.py`
- Run GTA game: `python saiyanquest/gta_game.py`
"""
    
    with open("development/README.md", "w") as f:
        f.write(readme_content)
    
    print("   ✅ Development workspace created")

def main():
    """Main setup function"""
    print("🎮 SaiyanQuest GTA - Development Setup")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Dependency check failed")
        return
    
    # Setup issue tracker
    tracker = setup_issue_tracker()
    
    # Create development workspace
    create_development_workspace()
    
    # Show next steps
    show_next_steps(tracker)
    
    print("\n🎉 Development environment ready!")
    print("\nTo start development:")
    print("1. Run: python issue_tracker.py")
    print("2. Start with Issue #1: Physics System Upgrade")
    print("3. Follow the systematic development approach")

if __name__ == "__main__":
    main()