#!/usr/bin/env python3
"""
SaiyanQuest Game Systems Launcher
Choose which system to test/run
"""

import sys
import subprocess
import os

def show_menu():
    """Show the available systems menu"""
    print("\n" + "="*60)
    print("🎮 SaiyanQuest Game Systems Launcher")
    print("="*60)
    print()
    print("Available Systems:")
    print()
    print("1. 📱 Main SaiyanQuest Game (Original)")
    print("   - Full original game with all features")
    print()
    print("2. 👤 Advanced Character/Pedestrian System") 
    print("   - Interactive characters with AI personalities")
    print("   - Physics, ragdoll effects, conversations")
    print("   - Controls: WASD, E to interact")
    print()
    print("3. 🚗 Enhanced Vehicle System")
    print("   - Advanced vehicle physics and controls") 
    print("   - Electrical/mechanical systems")
    print("   - Multiple vehicle types")
    print()
    print("4. 🌍 3D World System with Layers")
    print("   - Multi-layered 3D world rendering")
    print("   - Camera controls (WASD + Q/E)")
    print("   - Dynamic object management")
    print()
    print("5. 🗺️ Map Data Loading and Streaming")
    print("   - Large world chunk loading/unloading")
    print("   - Memory management and LOD system") 
    print("   - Performance monitoring")
    print()
    print("6. ✨ Vehicle Effects System")
    print("   - Particle systems and visual effects")
    print("   - Tire smoke, engine exhaust, brake effects")
    print()
    print("0. Exit")
    print("="*60)

def run_system(choice):
    """Run the selected system"""
    systems = {
        "1": {
            "name": "Main SaiyanQuest Game",
            "command": ["uv", "run", "python", "-m", "saiyanquest"],
            "description": "Running main SaiyanQuest game..."
        },
        "2": {
            "name": "Character System",
            "command": ["uv", "run", "python", "test_character_system.py"],
            "description": "Running character system test (30 seconds)..."
        },
        "3": {
            "name": "Vehicle System", 
            "command": ["uv", "run", "python", "test_vehicle_systems.py"],
            "description": "Running vehicle system test (30 seconds)..."
        },
        "4": {
            "name": "3D World System",
            "command": ["uv", "run", "python", "test_world_3d_system.py"],
            "description": "Running 3D world system test (30 seconds)..."
        },
        "5": {
            "name": "Map Streaming System",
            "command": ["uv", "run", "python", "test_map_data_streaming.py"],
            "description": "Running map streaming test (30 seconds)..."
        },
        "6": {
            "name": "Vehicle Effects System",
            "command": ["uv", "run", "python", "test_vehicle_effects.py"],
            "description": "Running vehicle effects test (30 seconds)..."
        }
    }
    
    if choice not in systems:
        print("❌ Invalid choice!")
        return False
    
    system = systems[choice]
    print(f"\n🚀 {system['description']}")
    print("💡 Press Escape to exit any test early")
    print("-" * 50)
    
    # Set up environment
    env = os.environ.copy()
    env["DISPLAY"] = ":0.0"
    
    try:
        # Run the system
        result = subprocess.run(system["command"], env=env)
        
        if result.returncode == 0:
            print(f"\n✅ {system['name']} completed successfully!")
        else:
            print(f"\n⚠️ {system['name']} exited with code {result.returncode}")
            
    except KeyboardInterrupt:
        print(f"\n🛑 {system['name']} interrupted by user")
    except Exception as e:
        print(f"\n❌ Error running {system['name']}: {e}")
    
    return True

def main():
    """Main launcher loop"""
    print("🎮 Welcome to SaiyanQuest!")
    
    while True:
        show_menu()
        
        try:
            choice = input("\n👉 Enter your choice (0-6): ").strip()
            
            if choice == "0":
                print("\n👋 Thanks for playing SaiyanQuest!")
                break
            
            if choice in ["1", "2", "3", "4", "5", "6"]:
                run_system(choice)
                input("\n📱 Press Enter to return to menu...")
            else:
                print("\n❌ Invalid choice! Please enter 0-6")
                input("📱 Press Enter to continue...")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except EOFError:
            print("\n\n👋 Goodbye!")
            break

if __name__ == "__main__":
    main()