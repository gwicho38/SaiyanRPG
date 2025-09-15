#!/usr/bin/env python3
"""
Run SaiyanQuest GTA with Pixel Art Maps
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main entry point"""
    print("🎮 SaiyanQuest GTA - Pixel Art Edition")
    print("=" * 50)
    
    try:
        from saiyanquest.gta_pixel_integration import run_pixel_art_demo
        
        success = run_pixel_art_demo()
        return 0 if success else 1
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running from the project root directory")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())