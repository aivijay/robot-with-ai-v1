"""
Robot memory - stores what the robot has learned about its environment.
Uses a simple JSON-based persistent storage.
"""
import json
import os
import time
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field, asdict
from pathlib import Path


@dataclass
class ObjectObservation:
    """An object the robot has seen."""
    object_type: str       # "chair", "box", "wall", "person", etc.
    first_seen: float      # timestamp
    last_seen: float       # timestamp
    location: str          # "kitchen", "living_room", "unknown"
    position: dict         # {"x": 0, "y": 0} relative to robot start
    observations: int      # how many times seen
    features: dict         # color, size, etc.


@dataclass
class AreaMap:
    """Map of an area the robot has explored."""
    name: str              # "kitchen", "bedroom", "unknown"
    explored_time: float   # when first explored
    last_visited: float    # last time visited
    visits: int            # number of visits
    objects: List[str]     # list of object types seen here
    boundaries: List[dict] # known walls/edges
    paths: List[dict]      # known paths between areas


@dataclass
class RobotMemory:
    """
    Long-term memory for the robot.
    Stores: objects seen, areas explored, learned skills.
    """
    # Identity
    name: str = "robot"
    created_at: float = field(default_factory=time.time)
    
    # Spatial memory
    current_area: str = "unknown"
    start_position: dict = field(default_factory=lambda: {"x": 0, "y": 0})
    current_position: dict = field(default_factory=lambda: {"x": 0, "y": 0})
    
    # Objects and areas
    objects: List[ObjectObservation] = field(default_factory=list)
    areas: List[AreaMap] = field(default_factory=list)
    
    # Skills learned
    skills: List[str] = field(default_factory=list)
    
    # Recent events (for context)
    recent_events: List[dict] = field(default_factory=list)
    
    def add_object(self, obj_type: str, features: dict = None):
        """Add or update an object observation."""
        now = time.time()
        
        # Check if already known
        for obj in self.objects:
            if obj.object_type == obj_type:
                obj.last_seen = now
                obj.observations += 1
                if features:
                    obj.features.update(features)
                return
                
        # New object
        new_obj = ObjectObservation(
            object_type=obj_type,
            first_seen=now,
            last_seen=now,
            location=self.current_area,
            position=dict(self.current_position),
            observations=1,
            features=features or {}
        )
        self.objects.append(new_obj)
        
    def add_area(self, area_name: str):
        """Mark an area as explored."""
        now = time.time()
        
        for area in self.areas:
            if area.name == area_name:
                area.last_visited = now
                area.visits += 1
                return
                
        new_area = AreaMap(
            name=area_name,
            explored_time=now,
            last_visited=now,
            visits=1,
            objects=[],
            boundaries=[],
            paths=[]
        )
        self.areas.append(new_area)
        self.current_area = area_name
        
    def add_event(self, event_type: str, details: dict = None):
        """Log a recent event."""
        event = {
            "type": event_type,
            "time": time.time(),
            "details": details or {}
        }
        self.recent_events.append(event)
        # Keep only last 50 events
        if len(self.recent_events) > 50:
            self.recent_events = self.recent_events[-50:]
            
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "created_at": self.created_at,
            "current_area": self.current_area,
            "start_position": self.start_position,
            "current_position": self.current_position,
            "objects": [asdict(o) for o in self.objects],
            "areas": [asdict(a) for a in self.areas],
            "skills": self.skills,
            "recent_events": self.recent_events
        }
        
    @classmethod
    def from_dict(cls, data: dict) -> 'RobotMemory':
        """Load from dictionary."""
        memory = cls()
        memory.name = data.get("name", "robot")
        memory.created_at = data.get("created_at", time.time())
        memory.current_area = data.get("current_area", "unknown")
        memory.start_position = data.get("start_position", {"x": 0, "y": 0})
        memory.current_position = data.get("current_position", {"x": 0, "y": 0})
        
        memory.objects = [ObjectObservation(**o) for o in data.get("objects", [])]
        memory.areas = [AreaMap(**a) for a in data.get("areas", [])]
        memory.skills = data.get("skills", [])
        memory.recent_events = data.get("recent_events", [])
        
        return memory


class MemoryStore:
    """
    Persistent memory storage for the robot.
    Loads and saves memory to disk.
    """
    
    def __init__(self, storage_path: str = "/home/vijay/projects/robot-with-ai-v1/src/memory/robot_memory.json"):
        self.storage_path = Path(storage_path)
        self.memory: Optional[RobotMemory] = None
        
    def load(self) -> RobotMemory:
        """Load memory from disk, or create new if none exists."""
        if self.memory is not None:
            return self.memory
            
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                self.memory = RobotMemory.from_dict(data)
                print(f"[Memory] Loaded from {self.storage_path}")
            except Exception as e:
                print(f"[Memory] Failed to load: {e}, creating new")
                self.memory = RobotMemory()
        else:
            self.memory = RobotMemory()
            print("[Memory] Created new robot memory")
            
        return self.memory
    
    def save(self):
        """Save memory to disk."""
        if self.memory is None:
            return
            
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(self.memory.to_dict(), f, indent=2)
            print(f"[Memory] Saved to {self.storage_path}")
        except Exception as e:
            print(f"[Memory] Failed to save: {e}")
            
    def update_position(self, x: float, y: float):
        """Update robot's current position estimate."""
        if self.memory:
            self.memory.current_position = {"x": x, "y": y}
            
    def learn_skill(self, skill_name: str):
        """Mark a skill as learned."""
        if self.memory and skill_name not in self.memory.skills:
            self.memory.skills.append(skill_name)
            print(f"[Memory] Learned skill: {skill_name}")
