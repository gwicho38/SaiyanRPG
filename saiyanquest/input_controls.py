#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
# Enhanced Input & Controls System with Gamepad Support

import json
import time
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("Warning: pygame not available, using mock input system")


class InputAction(Enum):
    """Input actions that can be bound to keys/buttons"""
    MOVE_UP = "move_up"
    MOVE_DOWN = "move_down"
    MOVE_LEFT = "move_left"
    MOVE_RIGHT = "move_right"
    THROTTLE = "throttle"
    BRAKE = "brake"
    STEERING_LEFT = "steering_left"
    STEERING_RIGHT = "steering_right"
    HANDBRAKE = "handbrake"
    HORN = "horn"
    FIRE = "fire"
    AIM = "aim"
    RELOAD = "reload"
    NEXT_WEAPON = "next_weapon"
    PREV_WEAPON = "prev_weapon"
    ENTER_EXIT_VEHICLE = "enter_exit_vehicle"
    INTERACT = "interact"
    JUMP = "jump"
    CROUCH = "crouch"
    SPRINT = "sprint"
    MENU = "menu"
    PAUSE = "pause"
    CONSOLE = "console"


class InputDevice(Enum):
    """Input device types"""
    KEYBOARD = "keyboard"
    MOUSE = "mouse"
    GAMEPAD = "gamepad"


class ControlScheme(Enum):
    """Control scheme presets"""
    KEYBOARD_MOUSE = "keyboard_mouse"
    GAMEPAD_CLASSIC = "gamepad_classic"
    GAMEPAD_MODERN = "gamepad_modern"
    CUSTOM = "custom"


@dataclass
class InputBinding:
    """Input binding configuration"""
    action: InputAction
    device: InputDevice
    key_code: int
    modifier_keys: List[str] = None
    deadzone: float = 0.1
    sensitivity: float = 1.0
    is_analog: bool = False
    is_inverted: bool = False


@dataclass
class InputState:
    """Current input state"""
    actions: Dict[InputAction, float]  # Action -> value (0.0 to 1.0)
    mouse_position: Tuple[float, float]
    mouse_delta: Tuple[float, float]
    gamepad_axes: Dict[int, float]
    gamepad_buttons: Dict[int, bool]
    last_input_time: float


class GamepadManager:
    """Gamepad/controller management"""
    
    def __init__(self):
        self.gamepads: Dict[int, Any] = {}
        self.gamepad_axes: Dict[int, Dict[int, float]] = {}
        self.gamepad_buttons: Dict[int, Dict[int, bool]] = {}
        self.gamepad_hats: Dict[int, Dict[int, Tuple[int, int]]] = {}
        
        # Gamepad button mappings (Xbox controller)
        self.button_mappings = {
            'A': 0, 'B': 1, 'X': 2, 'Y': 3,
            'LB': 4, 'RB': 5, 'BACK': 6, 'START': 7,
            'L3': 8, 'R3': 9, 'GUIDE': 10
        }
        
        # Gamepad axis mappings
        self.axis_mappings = {
            'LEFT_X': 0, 'LEFT_Y': 1,
            'RIGHT_X': 2, 'RIGHT_Y': 3,
            'LEFT_TRIGGER': 4, 'RIGHT_TRIGGER': 5
        }
        
        self._initialize_gamepads()
    
    def _initialize_gamepads(self):
        """Initialize connected gamepads"""
        if not PYGAME_AVAILABLE:
            print("⚠️ Gamepad support requires pygame")
            return
        
        pygame.joystick.init()
        num_joysticks = pygame.joystick.get_count()
        
        for i in range(num_joysticks):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()
            
            self.gamepads[i] = joystick
            self.gamepad_axes[i] = {}
            self.gamepad_buttons[i] = {}
            self.gamepad_hats[i] = {}
            
            print(f"🎮 Initialized gamepad {i}: {joystick.get_name()}")
    
    def update_gamepad_state(self, gamepad_id: int):
        """Update gamepad state"""
        if gamepad_id not in self.gamepads:
            return
        
        joystick = self.gamepads[gamepad_id]
        
        # Update axes
        for axis_id in range(joystick.get_numaxes()):
            value = joystick.get_axis(axis_id)
            self.gamepad_axes[gamepad_id][axis_id] = value
        
        # Update buttons
        for button_id in range(joystick.get_numbuttons()):
            pressed = joystick.get_button(button_id)
            self.gamepad_buttons[gamepad_id][button_id] = pressed
        
        # Update hats (D-pads)
        for hat_id in range(joystick.get_numhats()):
            hat_value = joystick.get_hat(hat_id)
            self.gamepad_hats[gamepad_id][hat_id] = hat_value
    
    def get_gamepad_axis(self, gamepad_id: int, axis_name: str) -> float:
        """Get gamepad axis value"""
        if gamepad_id not in self.gamepad_axes:
            return 0.0
        
        axis_id = self.axis_mappings.get(axis_name, -1)
        if axis_id == -1:
            return 0.0
        
        return self.gamepad_axes[gamepad_id].get(axis_id, 0.0)
    
    def get_gamepad_button(self, gamepad_id: int, button_name: str) -> bool:
        """Get gamepad button state"""
        if gamepad_id not in self.gamepad_buttons:
            return False
        
        button_id = self.button_mappings.get(button_name, -1)
        if button_id == -1:
            return False
        
        return self.gamepad_buttons[gamepad_id].get(button_id, False)


class InputManager:
    """Main input management system"""
    
    def __init__(self):
        self.input_bindings: Dict[InputAction, List[InputBinding]] = {}
        self.input_state = InputState(
            actions={},
            mouse_position=(0.0, 0.0),
            mouse_delta=(0.0, 0.0),
            gamepad_axes={},
            gamepad_buttons={},
            last_input_time=0.0
        )
        
        # Control schemes
        self.current_scheme = ControlScheme.KEYBOARD_MOUSE
        self.control_schemes: Dict[ControlScheme, Dict[InputAction, List[InputBinding]]] = {}
        
        # Gamepad manager
        self.gamepad_manager = GamepadManager()
        
        # Input callbacks
        self.input_callbacks: Dict[InputAction, List[Callable]] = {}
        
        # Settings
        self.mouse_sensitivity = 1.0
        self.gamepad_sensitivity = 1.0
        self.gamepad_deadzone = 0.15
        
        # Initialize default bindings
        self._initialize_default_bindings()
        
        print("🎮 InputManager initialized")
    
    def _initialize_default_bindings(self):
        """Initialize default input bindings"""
        # Keyboard bindings
        keyboard_bindings = {
            InputAction.MOVE_UP: [InputBinding(InputAction.MOVE_UP, InputDevice.KEYBOARD, pygame.K_w if PYGAME_AVAILABLE else 119)],
            InputAction.MOVE_DOWN: [InputBinding(InputAction.MOVE_DOWN, InputDevice.KEYBOARD, pygame.K_s if PYGAME_AVAILABLE else 115)],
            InputAction.MOVE_LEFT: [InputBinding(InputAction.MOVE_LEFT, InputDevice.KEYBOARD, pygame.K_a if PYGAME_AVAILABLE else 97)],
            InputAction.MOVE_RIGHT: [InputBinding(InputAction.MOVE_RIGHT, InputDevice.KEYBOARD, pygame.K_d if PYGAME_AVAILABLE else 100)],
            InputAction.THROTTLE: [InputBinding(InputAction.THROTTLE, InputDevice.KEYBOARD, pygame.K_w if PYGAME_AVAILABLE else 119)],
            InputAction.BRAKE: [InputBinding(InputAction.BRAKE, InputDevice.KEYBOARD, pygame.K_s if PYGAME_AVAILABLE else 115)],
            InputAction.STEERING_LEFT: [InputBinding(InputAction.STEERING_LEFT, InputDevice.KEYBOARD, pygame.K_a if PYGAME_AVAILABLE else 97)],
            InputAction.STEERING_RIGHT: [InputBinding(InputAction.STEERING_RIGHT, InputDevice.KEYBOARD, pygame.K_d if PYGAME_AVAILABLE else 100)],
            InputAction.HANDBRAKE: [InputBinding(InputAction.HANDBRAKE, InputDevice.KEYBOARD, pygame.K_SPACE if PYGAME_AVAILABLE else 32)],
            InputAction.HORN: [InputBinding(InputAction.HORN, InputDevice.KEYBOARD, pygame.K_h if PYGAME_AVAILABLE else 104)],
            InputAction.FIRE: [InputBinding(InputAction.FIRE, InputDevice.MOUSE, 1)],  # Left mouse button
            InputAction.AIM: [InputBinding(InputAction.AIM, InputDevice.MOUSE, 3)],  # Right mouse button
            InputAction.RELOAD: [InputBinding(InputAction.RELOAD, InputDevice.KEYBOARD, pygame.K_r if PYGAME_AVAILABLE else 114)],
            InputAction.NEXT_WEAPON: [InputBinding(InputAction.NEXT_WEAPON, InputDevice.KEYBOARD, pygame.K_TAB if PYGAME_AVAILABLE else 9)],
            InputAction.PREV_WEAPON: [InputBinding(InputAction.PREV_WEAPON, InputDevice.KEYBOARD, pygame.K_q if PYGAME_AVAILABLE else 113)],
            InputAction.ENTER_EXIT_VEHICLE: [InputBinding(InputAction.ENTER_EXIT_VEHICLE, InputDevice.KEYBOARD, pygame.K_e if PYGAME_AVAILABLE else 101)],
            InputAction.INTERACT: [InputBinding(InputAction.INTERACT, InputDevice.KEYBOARD, pygame.K_e if PYGAME_AVAILABLE else 101)],
            InputAction.JUMP: [InputBinding(InputAction.JUMP, InputDevice.KEYBOARD, pygame.K_SPACE if PYGAME_AVAILABLE else 32)],
            InputAction.CROUCH: [InputBinding(InputAction.CROUCH, InputDevice.KEYBOARD, pygame.K_LCTRL if PYGAME_AVAILABLE else 306)],
            InputAction.SPRINT: [InputBinding(InputAction.SPRINT, InputDevice.KEYBOARD, pygame.K_LSHIFT if PYGAME_AVAILABLE else 304)],
            InputAction.MENU: [InputBinding(InputAction.MENU, InputDevice.KEYBOARD, pygame.K_ESCAPE if PYGAME_AVAILABLE else 27)],
            InputAction.PAUSE: [InputBinding(InputAction.PAUSE, InputDevice.KEYBOARD, pygame.K_p if PYGAME_AVAILABLE else 112)],
            InputAction.CONSOLE: [InputBinding(InputAction.CONSOLE, InputDevice.KEYBOARD, pygame.K_BACKQUOTE if PYGAME_AVAILABLE else 96)]
        }
        
        # Gamepad bindings
        gamepad_bindings = {
            InputAction.THROTTLE: [InputBinding(InputAction.THROTTLE, InputDevice.GAMEPAD, 1, is_analog=True)],  # Right trigger
            InputAction.BRAKE: [InputBinding(InputAction.BRAKE, InputDevice.GAMEPAD, 0, is_analog=True)],  # Left trigger
            InputAction.STEERING_LEFT: [InputBinding(InputAction.STEERING_LEFT, InputDevice.GAMEPAD, 0, is_analog=True)],  # Left stick X
            InputAction.STEERING_RIGHT: [InputBinding(InputAction.STEERING_RIGHT, InputDevice.GAMEPAD, 0, is_analog=True)],  # Left stick X
            InputAction.HANDBRAKE: [InputBinding(InputAction.HANDBRAKE, InputDevice.GAMEPAD, 4)],  # LB
            InputAction.HORN: [InputBinding(InputAction.HORN, InputDevice.GAMEPAD, 5)],  # RB
            InputAction.FIRE: [InputBinding(InputAction.FIRE, InputDevice.GAMEPAD, 0)],  # A
            InputAction.AIM: [InputBinding(InputAction.AIM, InputDevice.GAMEPAD, 1)],  # B
            InputAction.RELOAD: [InputBinding(InputAction.RELOAD, InputDevice.GAMEPAD, 2)],  # X
            InputAction.NEXT_WEAPON: [InputBinding(InputAction.NEXT_WEAPON, InputDevice.GAMEPAD, 3)],  # Y
            InputAction.ENTER_EXIT_VEHICLE: [InputBinding(InputAction.ENTER_EXIT_VEHICLE, InputDevice.GAMEPAD, 0)],  # A
            InputAction.INTERACT: [InputBinding(InputAction.INTERACT, InputDevice.GAMEPAD, 0)],  # A
            InputAction.JUMP: [InputBinding(InputAction.JUMP, InputDevice.GAMEPAD, 0)],  # A
            InputAction.CROUCH: [InputBinding(InputAction.CROUCH, InputDevice.GAMEPAD, 8)],  # L3
            InputAction.SPRINT: [InputBinding(InputAction.SPRINT, InputDevice.GAMEPAD, 9)],  # R3
            InputAction.MENU: [InputBinding(InputAction.MENU, InputDevice.GAMEPAD, 6)],  # BACK
            InputAction.PAUSE: [InputBinding(InputAction.PAUSE, InputDevice.GAMEPAD, 7)]  # START
        }
        
        # Store control schemes
        self.control_schemes[ControlScheme.KEYBOARD_MOUSE] = keyboard_bindings
        self.control_schemes[ControlScheme.GAMEPAD_CLASSIC] = gamepad_bindings
        self.control_schemes[ControlScheme.GAMEPAD_MODERN] = gamepad_bindings  # Same for now
        
        # Set current bindings
        self.input_bindings = keyboard_bindings.copy()
    
    def set_control_scheme(self, scheme: ControlScheme):
        """Set the current control scheme"""
        if scheme in self.control_schemes:
            self.current_scheme = scheme
            self.input_bindings = self.control_schemes[scheme].copy()
            print(f"🎮 Control scheme set to {scheme.value}")
        else:
            print(f"❌ Unknown control scheme: {scheme.value}")
    
    def add_input_binding(self, action: InputAction, binding: InputBinding):
        """Add an input binding"""
        if action not in self.input_bindings:
            self.input_bindings[action] = []
        
        self.input_bindings[action].append(binding)
        print(f"🎮 Added binding for {action.value}")
    
    def remove_input_binding(self, action: InputAction, binding: InputBinding):
        """Remove an input binding"""
        if action in self.input_bindings:
            if binding in self.input_bindings[action]:
                self.input_bindings[action].remove(binding)
                print(f"🎮 Removed binding for {action.value}")
    
    def update_input_state(self, dt: float) -> InputState:
        """Update input state from all devices"""
        current_time = time.time()
        
        # Reset input state
        for action in InputAction:
            self.input_state.actions[action] = 0.0
        
        # Update keyboard input
        self._update_keyboard_input()
        
        # Update mouse input
        self._update_mouse_input()
        
        # Update gamepad input
        self._update_gamepad_input()
        
        # Update last input time
        if any(value > 0.0 for value in self.input_state.actions.values()):
            self.input_state.last_input_time = current_time
        
        return self.input_state
    
    def _update_keyboard_input(self):
        """Update keyboard input state"""
        if not PYGAME_AVAILABLE:
            return
        
        keys = pygame.key.get_pressed()
        
        for action, bindings in self.input_bindings.items():
            for binding in bindings:
                if binding.device == InputDevice.KEYBOARD:
                    if keys[binding.key_code]:
                        self.input_state.actions[action] = 1.0
                        break
    
    def _update_mouse_input(self):
        """Update mouse input state"""
        if not PYGAME_AVAILABLE:
            return
        
        mouse_buttons = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        
        # Update mouse position
        self.input_state.mouse_position = mouse_pos
        
        # Update mouse button states
        for action, bindings in self.input_bindings.items():
            for binding in bindings:
                if binding.device == InputDevice.MOUSE:
                    if binding.key_code < len(mouse_buttons) and mouse_buttons[binding.key_code]:
                        self.input_state.actions[action] = 1.0
                        break
    
    def _update_gamepad_input(self):
        """Update gamepad input state"""
        if not PYGAME_AVAILABLE:
            return
        
        # Update all connected gamepads
        for gamepad_id in self.gamepad_manager.gamepads.keys():
            self.gamepad_manager.update_gamepad_state(gamepad_id)
        
        # Process gamepad input for primary gamepad (ID 0)
        if 0 in self.gamepad_manager.gamepads:
            self._process_gamepad_input(0)
    
    def _process_gamepad_input(self, gamepad_id: int):
        """Process input from a specific gamepad"""
        for action, bindings in self.input_bindings.items():
            for binding in bindings:
                if binding.device == InputDevice.GAMEPAD:
                    value = 0.0
                    
                    if binding.is_analog:
                        # Analog input (triggers, sticks)
                        if binding.key_code == 0:  # Left stick X
                            value = self.gamepad_manager.get_gamepad_axis(gamepad_id, 'LEFT_X')
                        elif binding.key_code == 1:  # Right trigger
                            value = self.gamepad_manager.get_gamepad_axis(gamepad_id, 'RIGHT_TRIGGER')
                        elif binding.key_code == 0:  # Left trigger
                            value = self.gamepad_manager.get_gamepad_axis(gamepad_id, 'LEFT_TRIGGER')
                        
                        # Apply deadzone
                        if abs(value) < self.gamepad_deadzone:
                            value = 0.0
                        
                        # Apply sensitivity
                        value *= self.gamepad_sensitivity
                        
                        # Handle inverted axes
                        if binding.is_inverted:
                            value = -value
                    else:
                        # Digital input (buttons)
                        button_names = ['A', 'B', 'X', 'Y', 'LB', 'RB', 'BACK', 'START', 'L3', 'R3']
                        if binding.key_code < len(button_names):
                            button_name = button_names[binding.key_code]
                            if self.gamepad_manager.get_gamepad_button(gamepad_id, button_name):
                                value = 1.0
                    
                    # Update action value
                    if value != 0.0:
                        self.input_state.actions[action] = max(
                            self.input_state.actions[action], abs(value)
                        )
    
    def get_action_value(self, action: InputAction) -> float:
        """Get the current value of an action"""
        return self.input_state.actions.get(action, 0.0)
    
    def is_action_pressed(self, action: InputAction) -> bool:
        """Check if an action is currently pressed"""
        return self.get_action_value(action) > 0.1
    
    def get_movement_vector(self) -> Tuple[float, float]:
        """Get movement vector from input"""
        x = 0.0
        y = 0.0
        
        if self.is_action_pressed(InputAction.MOVE_LEFT):
            x -= 1.0
        if self.is_action_pressed(InputAction.MOVE_RIGHT):
            x += 1.0
        if self.is_action_pressed(InputAction.MOVE_UP):
            y -= 1.0
        if self.is_action_pressed(InputAction.MOVE_DOWN):
            y += 1.0
        
        return (x, y)
    
    def get_vehicle_inputs(self) -> Dict[str, Any]:
        """Get vehicle control inputs"""
        throttle = self.get_action_value(InputAction.THROTTLE)
        brake = self.get_action_value(InputAction.BRAKE)
        
        # Steering from left/right or gamepad stick
        steering_left = self.get_action_value(InputAction.STEERING_LEFT)
        steering_right = self.get_action_value(InputAction.STEERING_RIGHT)
        steering = steering_right - steering_left
        
        handbrake = self.is_action_pressed(InputAction.HANDBRAKE)
        horn = self.is_action_pressed(InputAction.HORN)
        
        return {
            'throttle': throttle,
            'brake': brake,
            'steering': steering,
            'handbrake': handbrake,
            'horn': horn
        }
    
    def get_weapon_inputs(self) -> Dict[str, Any]:
        """Get weapon control inputs"""
        fire = self.is_action_pressed(InputAction.FIRE)
        aim = self.is_action_pressed(InputAction.AIM)
        reload = self.is_action_pressed(InputAction.RELOAD)
        next_weapon = self.is_action_pressed(InputAction.NEXT_WEAPON)
        prev_weapon = self.is_action_pressed(InputAction.PREV_WEAPON)
        
        return {
            'fire': fire,
            'aim': aim,
            'reload': reload,
            'next_weapon': next_weapon,
            'prev_weapon': prev_weapon
        }
    
    def get_interaction_inputs(self) -> Dict[str, Any]:
        """Get interaction inputs"""
        enter_exit_vehicle = self.is_action_pressed(InputAction.ENTER_EXIT_VEHICLE)
        interact = self.is_action_pressed(InputAction.INTERACT)
        jump = self.is_action_pressed(InputAction.JUMP)
        crouch = self.is_action_pressed(InputAction.CROUCH)
        sprint = self.is_action_pressed(InputAction.SPRINT)
        
        return {
            'enter_exit_vehicle': enter_exit_vehicle,
            'interact': interact,
            'jump': jump,
            'crouch': crouch,
            'sprint': sprint
        }
    
    def save_bindings(self, filename: str):
        """Save input bindings to file"""
        bindings_data = {}
        
        for action, bindings in self.input_bindings.items():
            bindings_data[action.value] = []
            for binding in bindings:
                binding_data = {
                    'device': binding.device.value,
                    'key_code': binding.key_code,
                    'deadzone': binding.deadzone,
                    'sensitivity': binding.sensitivity,
                    'is_analog': binding.is_analog,
                    'is_inverted': binding.is_inverted
                }
                bindings_data[action.value].append(binding_data)
        
        with open(filename, 'w') as f:
            json.dump(bindings_data, f, indent=2)
        
        print(f"🎮 Saved input bindings to {filename}")
    
    def load_bindings(self, filename: str):
        """Load input bindings from file"""
        try:
            with open(filename, 'r') as f:
                bindings_data = json.load(f)
            
            self.input_bindings = {}
            
            for action_name, bindings_list in bindings_data.items():
                action = InputAction(action_name)
                self.input_bindings[action] = []
                
                for binding_data in bindings_list:
                    binding = InputBinding(
                        action=action,
                        device=InputDevice(binding_data['device']),
                        key_code=binding_data['key_code'],
                        deadzone=binding_data.get('deadzone', 0.1),
                        sensitivity=binding_data.get('sensitivity', 1.0),
                        is_analog=binding_data.get('is_analog', False),
                        is_inverted=binding_data.get('is_inverted', False)
                    )
                    self.input_bindings[action].append(binding)
            
            print(f"🎮 Loaded input bindings from {filename}")
            
        except Exception as e:
            print(f"❌ Failed to load input bindings: {e}")
    
    def get_input_statistics(self) -> Dict[str, Any]:
        """Get input system statistics"""
        active_actions = sum(1 for value in self.input_state.actions.values() if value > 0.0)
        
        return {
            'current_scheme': self.current_scheme.value,
            'active_actions': active_actions,
            'total_bindings': sum(len(bindings) for bindings in self.input_bindings.values()),
            'connected_gamepads': len(self.gamepad_manager.gamepads),
            'mouse_position': self.input_state.mouse_position,
            'last_input_time': self.input_state.last_input_time
        }


# Test the input system
if __name__ == "__main__":
    print("🧪 Testing Input System...")
    
    # Create input manager
    input_manager = InputManager()
    
    # Test different control schemes
    print("Testing keyboard/mouse scheme:")
    input_manager.set_control_scheme(ControlScheme.KEYBOARD_MOUSE)
    
    # Simulate some input
    for frame in range(60):  # 1 second at 60 FPS
        dt = 1.0 / 60.0
        
        # Update input state
        input_state = input_manager.update_input_state(dt)
        
        if frame % 30 == 0:  # Print every 0.5 seconds
            vehicle_inputs = input_manager.get_vehicle_inputs()
            weapon_inputs = input_manager.get_weapon_inputs()
            interaction_inputs = input_manager.get_interaction_inputs()
            
            print(f"  Frame {frame}:")
            print(f"    Vehicle: throttle={vehicle_inputs['throttle']:.2f}, "
                  f"brake={vehicle_inputs['brake']:.2f}, "
                  f"steering={vehicle_inputs['steering']:.2f}")
            print(f"    Weapon: fire={weapon_inputs['fire']}, "
                  f"aim={weapon_inputs['aim']}, "
                  f"reload={weapon_inputs['reload']}")
            print(f"    Interaction: enter_vehicle={interaction_inputs['enter_exit_vehicle']}, "
                  f"interact={interaction_inputs['interact']}")
    
    # Test gamepad scheme
    print("\nTesting gamepad scheme:")
    input_manager.set_control_scheme(ControlScheme.GAMEPAD_CLASSIC)
    
    # Get statistics
    stats = input_manager.get_input_statistics()
    print(f"Input statistics: {stats}")
    
    print("✅ Input System test completed")