#!/usr/bin/env python3
"""Wrapper script that runs robot_agent with proper Python path."""
import sys
import os

# Add parent of src to path (project root)
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

# Now import
from src.common.hardware import RobotConfig
from src.robot import CameraStream, MotorController, ReflexController, SkillLayer
from src.memory.robot_memory import MemoryStore
from src.agent.brain import AgentBrain

print("All imports OK!")
print(f"RobotConfig stby={RobotConfig.stby}")
