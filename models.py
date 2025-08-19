"""
Data models for narrative objects and relationships.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class Relationship:
    """Represents a relationship between narrative objects."""
    target: str
    description: str
    
    def __eq__(self, other):
        """Check equality based on target and description."""
        if not isinstance(other, Relationship):
            return False
        return self.target == other.target and self.description == other.description
    
    def __hash__(self):
        """Make Relationship hashable for use in sets."""
        return hash((self.target, self.description))


@dataclass
class NarrativeObject:
    """Represents a narrative object extracted from text."""
    name: str
    description: str
    relationships: List[Relationship] = field(default_factory=list)
    first_seen: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def __eq__(self, other):
        """Check equality based on name only."""
        if not isinstance(other, NarrativeObject):
            return False
        return self.name == other.name
    
    def __hash__(self):
        """Make NarrativeObject hashable for use in sets."""
        return hash(self.name)
    
    def update_from(self, other: 'NarrativeObject') -> bool:
        """
        Update this object with data from another object.
        
        Args:
            other: Another NarrativeObject with the same name
            
        Returns:
            True if any changes were made, False otherwise
        """
        if self.name != other.name:
            raise ValueError(f"Cannot update {self.name} with data from {other.name}")
        
        changed = False
        
        # Update description if different
        if self.description != other.description:
            self.description = other.description
            changed = True
        
        # Update relationships if different
        if set(self.relationships) != set(other.relationships):
            self.relationships = other.relationships.copy()
            changed = True
        
        if changed:
            self.last_updated = datetime.now()
        
        return changed
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "relationships": [
                {"target": rel.target, "description": rel.description}
                for rel in self.relationships
            ],
            "first_seen": self.first_seen.isoformat(),
            "last_updated": self.last_updated.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NarrativeObject':
        """Create from dictionary representation."""
        relationships = [
            Relationship(rel["target"], rel["description"])
            for rel in data.get("relationships", [])
        ]
        
        obj = cls(
            name=data["name"],
            description=data["description"],
            relationships=relationships
        )
        
        # Set timestamps if available
        if "first_seen" in data:
            obj.first_seen = datetime.fromisoformat(data["first_seen"])
        if "last_updated" in data:
            obj.last_updated = datetime.fromisoformat(data["last_updated"])
        
        return obj


@dataclass
class ObjectCollection:
    """Container for managing multiple narrative objects."""
    objects: Dict[str, NarrativeObject] = field(default_factory=dict)
    
    def add_or_update(self, obj: NarrativeObject) -> bool:
        """
        Add a new object or update an existing one.
        
        Args:
            obj: NarrativeObject to add or update
            
        Returns:
            True if object was added or updated, False if no changes
        """
        if obj.name in self.objects:
            return self.objects[obj.name].update_from(obj)
        else:
            self.objects[obj.name] = obj
            return True
    
    def remove(self, name: str) -> bool:
        """
        Remove an object by name.
        
        Args:
            name: Name of the object to remove
            
        Returns:
            True if object was removed, False if not found
        """
        if name in self.objects:
            del self.objects[name]
            return True
        return False
    
    def get(self, name: str) -> Optional[NarrativeObject]:
        """Get an object by name."""
        return self.objects.get(name)
    
    def list_all(self) -> List[NarrativeObject]:
        """Get all objects as a list."""
        return list(self.objects.values())
    
    def merge_from_list(self, new_objects: List[NarrativeObject], remove_missing: bool = False) -> Dict[str, str]:
        """
        Merge a list of objects with the current collection.
        
        Args:
            new_objects: List of NarrativeObject instances to merge
            remove_missing: If True, remove existing objects not in new_objects.
                          If False (default), preserve all existing objects.
            
        Returns:
            Dict with counts of changes: {"added": 2, "updated": 1, "unchanged": 3}
        """
        current_names = set(self.objects.keys())
        new_names = set(obj.name for obj in new_objects)
        
        added = 0
        updated = 0
        unchanged = 0
        removed = 0
        
        # Process new objects (add or update existing ones)
        for obj in new_objects:
            if self.add_or_update(obj):
                if obj.name in current_names:
                    updated += 1
                else:
                    added += 1
            else:
                unchanged += 1
        
        # Only remove objects if explicitly requested
        # This is more conservative - preserves narrative continuity
        if remove_missing:
            removed_names = current_names - new_names
            for name in removed_names:
                if self.remove(name):
                    removed += 1
        
        return {
            "added": added,
            "updated": updated, 
            "unchanged": unchanged,
            "removed": removed
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "objects": {name: obj.to_dict() for name, obj in self.objects.items()},
            "count": len(self.objects)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ObjectCollection':
        """Create from dictionary representation."""
        collection = cls()
        for name, obj_data in data.get("objects", {}).items():
            collection.objects[name] = NarrativeObject.from_dict(obj_data)
        return collection