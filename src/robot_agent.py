#!/usr/bin/env python3
"""
Robot Agent - Main entry point for autonomous robot.
Runs on Raspberry Pi.

Architecture:
1. Robot hardware (camera, motors)
2. Reflex layer (instant safety)
3. Skill layer (navigation commands)
4. Agent brain (LLM-powered thinking)
5. Memory (persistent storage)

Features:
- Stuck detection: After 4 consecutive forward attempts that get blocked,
  executes an escape maneuver (reverse -> turn -> forward)
"""
import sys
import os

# Add project root to path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

import time
import signal
import json
import threading
from pathlib import Path

from src.common.hardware import RobotConfig
from src.robot import CameraStream, MotorController, ReflexController, SkillLayer
from src.memory.robot_memory import MemoryStore
from src.agent.brain import AgentBrain
from src.robot.reflex import ReflexState


class RobotAgent:
    """
    Main robot agent - ties all systems together.
    """
    
    def __init__(self, config: RobotConfig = None):
        self.config = config or RobotConfig()
        self.camera = None
        self.motors = None
        self.reflex = None
        self.skills = None
        self.memory_store = None
        self.memory = None
        self.agent = None
        self._running = False
        
        # Stuck detection - counts consecutive times forward was blocked
        self._stuck_counter = 0
        self._stuck_threshold = 4  # After 4 blocked forwards, trigger escape
        self._escape_cooldown = 0  # Frames to wait after escape before counting again
        self._last_was_forward = False
        
        # Dashboard shared state file
        self._state_file = Path("/tmp/robot_state.json")
        self._state_lock = threading.Lock()
        
    def setup(self):
        """Initialize all robot systems."""
        print("=== Robot Agent v1.0 ===")
        
        print("[1/5] Setting up motors...")
        self.motors = MotorController(self.config)
        self.motors.setup()
        print("  Motors OK")
        
        print("[2/5] Starting camera stream...")
        self.camera = CameraStream(
            width=self.config.camera_width,
            height=self.config.camera_height
        )
        self.camera.start()
        print(f"  Camera OK ({self.camera.fps:.1f} fps)")
        
        print("[3/5] Starting reflex system...")
        self.reflex = ReflexController(self.config, self.camera, self.motors)
        self.reflex.start()
        print("  Reflex OK")
        
        print("[4/5] Loading memory...")
        self.memory_store = MemoryStore()
        self.memory = self.memory_store.load()
        print(f"  Memory: {len(self.memory.objects)} objects, {len(self.memory.areas)} areas")
        
        print("[5/5] Initializing agent brain...")
        self.skills = SkillLayer(self.motors, self.reflex, self.config)
        self.agent = AgentBrain(self.memory, self.reflex, self.skills, self.config)
        print("  Agent OK")
        
        print("\n=== Robot ready! ===")
        
    def run(self, duration: float = None):
        """
        Run the robot agent.
        If duration is None, runs forever (or until interrupted).
        """
        self._running = True
        start_time = time.time()
        
        # Reset stuck detection
        self._stuck_counter = 0
        self._escape_cooldown = 0
        self._last_was_forward = False
        
        # Set up signal handlers
        def signal_handler(sig, frame):
            print("\n[Agent] Interrupted!")
            self.stop()
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        print(f"\nRunning{' for ' + str(duration) + 's' if duration else ' indefinitely'}...")
        print("Press Ctrl+C to stop.\n")
        
        iteration = 0
        while self._running:
            iteration += 1
            
            # Agent thinks and acts
            if self.agent:
                reflex_state = self.reflex.state.value if self.reflex else "unknown"
                reflex_action = self.reflex.last_action if self.reflex else "none"
                floor_brightness = getattr(self.reflex, 'last_floor_brightness', 0)
                obstacle_score = getattr(self.reflex, 'last_obstacle_ratio', 0)
                
                # Update dashboard state
                self._update_dashboard_state(reflex_state, reflex_action, 
                                           floor_brightness, obstacle_score)
                
                observation = {
                    'fps': self.camera.fps if self.camera else 0,
                    'reflex_state': reflex_state,
                    'reflex_action': reflex_action
                }
                
                # Stuck detection logic
                was_blocked = (self.reflex.state.value == ReflexState.DANGER.value and 
                              self.reflex.last_action in ['stopped', 'slowed'])
                
                # Handle escape cooldown
                if self._escape_cooldown > 0:
                    self._escape_cooldown -= 1
                    self._stuck_counter = 0  # Reset counter during cooldown
                elif self._stuck_counter >= self._stuck_threshold:
                    # STUCK - execute escape maneuver
                    print(f"\n[Agent] *** STUCK DETECTED ({self._stuck_counter} blocks) - ESCAPING ***")
                    self._execute_escape()
                    self._stuck_counter = 0
                    self._escape_cooldown = 30  # ~10 seconds cooldown before counting again
                    continue  # Skip normal think/execute this iteration
                
                # Normal case: track forward attempts that were blocked
                action = self.agent.think(observation)
                
                # Check if action is a forward movement
                is_forward_action = action in ['wander_forward', 'explore_forward', 'forward']
                
                if is_forward_action and was_blocked:
                    self._stuck_counter += 1
                    print(f"[Agent] Forward blocked (count={self._stuck_counter}/{self._stuck_threshold})")
                    self._last_was_forward = True
                elif is_forward_action:
                    # Forward succeeded, reset counter
                    if self._last_was_forward:
                        self._stuck_counter = max(0, self._stuck_counter - 1)
                    self._last_was_forward = True
                else:
                    # Not a forward action, reset tracking
                    self._last_was_forward = False
                    
                self.agent.execute_action(action)
                
            # Log every 10 iterations
            if iteration % 10 == 0:
                status = self.agent.get_status() if self.agent else {}
                stuck_info = f" stuck={self._stuck_counter}/{self._stuck_threshold}" if self._stuck_counter > 0 else ""
                print(f"[Agent] iter={iteration} state={status.get('state', '?')} reflex={status.get('reflex', '?')}{stuck_info}")
                
            # Check duration limit
            if duration and (time.time() - start_time) >= duration:
                break
                
            time.sleep(0.1)
            
        print("\n[Agent] Run complete.")
        
    def _update_dashboard_state(self, reflex_state, reflex_action, floor_brightness, obstacle_score):
        """Write current state to shared file for dashboard."""
        state_data = {
            'reflex_state': reflex_state,
            'reflex_action': reflex_action,
            'floor_brightness': floor_brightness,
            'obstacle_score': obstacle_score,
            'stuck_counter': self._stuck_counter,
            'iteration': getattr(self, '_iteration', 0),
            'timestamp': time.time()
        }
        try:
            with open(self._state_file, 'w') as f:
                json.dump(state_data, f)
        except:
            pass
        
    def _execute_escape(self):
        """
        Execute an escape maneuver when stuck is detected.
        Does a sequence: reverse -> turn -> forward.
        """
        import random
        
        # First: reverse a bit
        print("[Agent]     -> reversing")
        self.skills.reverse(duration=1.0, speed=self.config.speed_slow)
        time.sleep(0.3)
        
        # Second: turn in a random direction
        direction = random.choice(["left", "right"])
        turn_duration = random.uniform(0.8, 1.5)  # Variable turn
        print(f"[Agent]     -> turning {direction} for {turn_duration:.1f}s")
        self.skills.turn(direction, duration=turn_duration, speed=self.config.speed_medium)
        time.sleep(0.3)
        
        # Third: try forward again
        print("[Agent]     -> forward attempt")
        self.skills.forward(duration=1.0, speed=self.config.speed_slow)
        
        print("[Agent]     escape complete")
        
    def stop(self):
        """Stop all robot systems gracefully."""
        print("\n[Agent] Shutting down...")
        self._running = False
        
        if self.reflex:
            self.reflex.stop()
            print("  Reflex stopped")
            
        if self.camera:
            self.camera.stop()
            print("  Camera stopped")
            
        if self.motors:
            self.motors.cleanup()
            print("  Motors stopped")
            
        if self.memory_store:
            self.memory_store.save()
            print("  Memory saved")
            
        print("\n[Agent] Goodbye!")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Robot Agent')
    parser.add_argument('--duration', '-d', type=float, default=None,
                        help='Run duration in seconds (default: indefinite)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output')
    args = parser.parse_args()
    
    config = RobotConfig()
    
    # Create and run agent
    agent = RobotAgent(config)
    
    try:
        agent.setup()
        agent.run(duration=args.duration)
    finally:
        agent.stop()


if __name__ == '__main__':
    main()
