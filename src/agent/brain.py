"""
Agent brain - the LLM-powered orchestrator.
This is the 'prefrontal cortex' - slow, deliberate thinking.

The agent observes the world through the reflex system,
decides what to do next, and executes skills.
"""
import time
import json
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum

from ..robot.reflex import ReflexController, ReflexState
from ..memory.robot_memory import RobotMemory, MemoryStore


class AgentState(Enum):
    IDLE = "idle"
    EXPLORING = "exploring"
    NAVIGATING = "navigating"
    AVOIDING = "avoiding"
    LEARNING = "learning"
    WAITING = "waiting"


@dataclass
class AgentThought:
    """A thought/decision from the agent."""
    timestamp: float
    situation: str           # What the agent observes
    reasoning: str           # Why it chose this action
    action: str              # What it decided to do
    result: str              # What happened


class AgentBrain:
    """
    LLM-powered agent brain.
    
    Observes:
    - Robot state (position, battery, sensors)
    - Reflex state (what dangers detected)
    - Memory (what robot has learned)
    
    Decides:
    - What skill to execute next
    - What to remember/learn
    
    The agent doesn't control motors directly -
    it tells the skill layer what to do.
    """
    
    def __init__(self, 
                 memory: RobotMemory,
                 reflex: ReflexController,
                 skills,
                 config):
        self.memory = memory
        self.reflex = reflex
        self.skills = skills
        self.config = config
        
        self.state = AgentState.IDLE
        self.thought_history: List[AgentThought] = []
        self.last_thought_time = 0
        self.think_interval = config.agent_think_interval
        
        # Wander state
        self._wander_active = False
        self._wander_counter = 0
        
        # LLM prompt template
        self._system_prompt = self._build_system_prompt()
        
    def _build_system_prompt(self) -> str:
        """Build the LLM system prompt."""
        return """You are a robot AI controlling a small autonomous vehicle.
You have two control layers:
1. FAST REFLEXES (automatic) - handles obstacle/cliff avoidance instantly
2. SLOW THINKING (you) - decides where to go, what to explore

You can call these skills:
- forward(duration, speed) - move forward
- reverse(duration, speed) - move backward  
- turn(direction, duration, speed) - turn in place left/right
- arc(direction, duration, speed) - arc turn left/right
- wait(duration) - pause

Your memory tells you what you've seen before.
Your reflex tells you what's happening NOW.

Decide what to do based on:
1. What you can see (reflex state)
2. What you've explored (memory)
3. What seems interesting (curiosity)

Be curious! Explore new areas. Remember what you see.
When you see an object, try to describe and remember it.
"""
        
    def think(self, observation: Dict[str, Any]) -> str:
        """
        Main thinking loop - called periodically by the agent loop.
        Returns the action/skill to execute.
        """
        now = time.time()
        
        # Don't think too often
        if now - self.last_thought_time < self.think_interval:
            return "wait"
        self.last_thought_time = now
        
        # Build observation summary
        reflex_state = self.reflex.state.value if self.reflex.state else "unknown"
        reflex_action = self.reflex.last_action
        floor_brightness = getattr(self.reflex, 'last_floor_brightness', 0)
        obstacle_ratio = getattr(self.reflex, 'last_obstacle_ratio', 0)
        
        # WANDER MODE: keep moving, explore
        if reflex_state == ReflexState.DANGER.value:
            situation = f"DANGER: reflex took {reflex_action}"
            reasoning = "Danger detected - reflex is handling it"
            action = "wait_for_clear"
        elif reflex_state == ReflexState.CAUTION.value:
            situation = f"CAUTION: floor={floor_brightness}, obs={obstacle_ratio:.2f}"
            reasoning = "Something ahead - slow down and turn"
            action = "wander_turn"
        else:
            situation = f"CLEAR: floor={floor_brightness}, obs={obstacle_ratio:.2f}"
            reasoning = "Path is clear - keep exploring forward"
            action = "wander_forward"
            
        # Build prompt for LLM
        prompt = f"""Current situation: {situation}
Reflex state: {reflex_state}
Last reflex action: {reflex_action}

{self._system_prompt}

What should the robot do now? Choose a skill to execute."""
        
        # Log the thought
        thought = AgentThought(
            timestamp=now,
            situation=situation,
            reasoning=reasoning,
            action=action,
            result="pending"
        )
        self.thought_history.append(thought)
        
        # Keep only last 20 thoughts
        if len(self.thought_history) > 20:
            self.thought_history = self.thought_history[-20:]
            
        return action
        
    def execute_action(self, action: str) -> bool:
        """
        Execute an action/skill.
        Returns True if successful, False if failed/stopped.
        """
        try:
            if action == "wander_forward":
                self.state = AgentState.EXPLORING
                self._wander_counter += 1
                print(f"[Agent] wander_forward #{self._wander_counter}")
                # Alternate between forward and slight turns to cover area
                if self._wander_counter % 3 == 0:
                    print("[Agent] -> arc right")
                    self.skills.arc("right", duration=0.8, speed=self.config.speed_slow)
                elif self._wander_counter % 3 == 1:
                    print("[Agent] -> arc left")
                    self.skills.arc("left", duration=0.8, speed=self.config.speed_slow)
                else:
                    print("[Agent] -> forward")
                    self.skills.forward(duration=0.5, speed=self.config.speed_medium)
                return True
                
            elif action == "wander_turn":
                self.state = AgentState.AVOIDING
                print("[Agent] wander_turn")
                # Turn away from obstacle
                import random
                direction = "left" if random.random() > 0.5 else "right"
                self.skills.turn(direction, duration=0.4, speed=self.config.speed_medium)
                return True
                
            elif action == "explore_forward":
                self.state = AgentState.EXPLORING
                print("[Agent] explore_forward -> arc right")
                # Arc slightly left to sweep area
                self.skills.arc("right", duration=2.0, speed=self.config.speed_medium)
                self.state = AgentState.IDLE
                return True
                
            elif action == "continue_slow":
                self.state = AgentState.AVOIDING
                self.skills.forward(duration=1.0, speed=self.config.speed_slow)
                self.state = AgentState.IDLE
                return True
                
            elif action == "wait_for_clear":
                self.state = AgentState.WAITING
                self.skills.wait(duration=0.5)
                self.state = AgentState.IDLE
                return True
                
            elif action == "turn_left":
                self.skills.turn("left", duration=0.5, speed=self.config.speed_medium)
                return True
                
            elif action == "turn_right":
                self.skills.turn("right", duration=0.5, speed=self.config.speed_medium)
                return True
                
            elif action == "reverse":
                self.state = AgentState.AVOIDING
                self.skills.reverse(duration=1.0, speed=self.config.speed_slow)
                self.state = AgentState.IDLE
                return True
                
            elif action == "wait":
                self.skills.wait(duration=self.think_interval)
                return True
                
            else:
                print(f"[Agent] Unknown action: {action}")
                return False
                
        except Exception as e:
            print(f"[Agent] Action failed: {e}")
            return False
            
    def observe_object(self, object_type: str, features: dict):
        """Remember an object the robot has seen."""
        self.memory.add_object(object_type, features)
        self.memory.add_event("saw_object", {"type": object_type, "features": features})
        
    def get_status(self) -> dict:
        """Get current agent status."""
        return {
            "state": self.state.value if self.state else "unknown",
            "thoughts": len(self.thought_history),
            "memory": {
                "areas": len(self.memory.areas),
                "objects": len(self.memory.objects),
                "skills": len(self.memory.skills)
            },
            "reflex": self.reflex.state.value if self.reflex.state else "unknown"
        }
