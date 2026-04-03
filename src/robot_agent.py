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
"""
import sys
import os

# Add project root to path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

import time
import signal

from src.common.hardware import RobotConfig
from src.robot import CameraStream, MotorController, ReflexController, SkillLayer
from src.memory.robot_memory import MemoryStore
from src.agent.brain import AgentBrain


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
                observation = {
                    'fps': self.camera.fps if self.camera else 0,
                    'reflex_state': self.reflex.state.value if self.reflex else "unknown",
                    'reflex_action': self.reflex.last_action if self.reflex else "none"
                }
                action = self.agent.think(observation)
                self.agent.execute_action(action)
                
            # Log every 10 iterations
            if iteration % 10 == 0:
                status = self.agent.get_status() if self.agent else {}
                print(f"[Agent] iter={iteration} state={status.get('state', '?')} reflex={status.get('reflex', '?')}")
                
            # Check duration limit
            if duration and (time.time() - start_time) >= duration:
                break
                
            time.sleep(0.1)
            
        print("\n[Agent] Run complete.")
        
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
