"""
Object manager for maintaining narrative object state.
"""
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from models import NarrativeObject, ObjectCollection
from narrative_parser import NarrativeParser


class ObjectManager:
    """Manages the state of narrative objects across text updates."""
    
    def __init__(self, save_file: Optional[str] = None):
        """
        Initialize the object manager.
        
        Args:
            save_file: Optional file path for persistence
        """
        self.collection = ObjectCollection()
        self.parser = NarrativeParser()
        self.save_file = save_file
        
        # Load from file if it exists
        if save_file and Path(save_file).exists():
            self.load_from_file(save_file)
    
    def process_text_update(self, text: str, llm_response: str) -> Dict[str, Any]:
        """
        Process a text update with LLM response.
        
        Args:
            text: The input text that was analyzed
            llm_response: Raw response from LLM
            
        Returns:
            Dictionary with update statistics and current objects
        """
        try:
            # Parse the LLM response
            new_objects = self.parser.parse_llm_response(llm_response)
            
            # Validate relationships
            new_objects = self.parser.validate_relationships(new_objects)
            
            # Merge with existing objects
            stats = self.collection.merge_from_list(new_objects)
            
            # Save state if configured
            if self.save_file:
                self.save_to_file(self.save_file)
            
            return {
                "success": True,
                "stats": stats,
                "objects": self.collection.list_all(),
                "total_count": len(self.collection.objects),
                "error": None
            }
            
        except Exception as e:
            return {
                "success": False,
                "stats": {"added": 0, "updated": 0, "unchanged": 0, "removed": 0},
                "objects": self.collection.list_all(),
                "total_count": len(self.collection.objects),
                "error": str(e)
            }
    
    def get_all_objects(self) -> List[NarrativeObject]:
        """Get all current narrative objects."""
        return self.collection.list_all()
    
    def get_object(self, name: str) -> Optional[NarrativeObject]:
        """Get a specific object by name."""
        return self.collection.get(name)
    
    def get_object_count(self) -> int:
        """Get the total number of objects."""
        return len(self.collection.objects)
    
    def clear_all_objects(self):
        """Clear all objects from memory."""
        self.collection = ObjectCollection()
        if self.save_file:
            self.save_to_file(self.save_file)
    
    def remove_object(self, name: str) -> bool:
        """
        Remove a specific object by name.
        
        Args:
            name: Name of the object to remove
            
        Returns:
            True if object was removed, False if not found
        """
        result = self.collection.remove(name)
        if result and self.save_file:
            self.save_to_file(self.save_file)
        return result
    
    def get_objects_summary(self) -> Dict[str, Any]:
        """Get a summary of current objects for display."""
        objects = self.collection.list_all()
        
        # Sort by last updated (most recent first)
        objects.sort(key=lambda x: x.last_updated, reverse=True)
        
        return {
            "total_count": len(objects),
            "objects": [
                {
                    "name": obj.name,
                    "description": obj.description,
                    "relationship_count": len(obj.relationships),
                    "relationships": [
                        {"target": rel.target, "description": rel.description}
                        for rel in obj.relationships
                    ],
                    "last_updated": obj.last_updated.isoformat()
                }
                for obj in objects
            ]
        }
    
    def save_to_file(self, file_path: str):
        """
        Save current state to a JSON file.
        
        Args:
            file_path: Path to save file
        """
        try:
            data = self.collection.to_dict()
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving to file {file_path}: {e}")
    
    def load_from_file(self, file_path: str) -> bool:
        """
        Load state from a JSON file.
        
        Args:
            file_path: Path to load from
            
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.collection = ObjectCollection.from_dict(data)
            return True
            
        except Exception as e:
            print(f"Error loading from file {file_path}: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get detailed statistics about the current object collection."""
        objects = self.collection.list_all()
        
        if not objects:
            return {
                "total_objects": 0,
                "total_relationships": 0,
                "avg_relationships_per_object": 0,
                "objects_with_relationships": 0,
                "oldest_object": None,
                "newest_object": None
            }
        
        # Calculate statistics
        total_relationships = sum(len(obj.relationships) for obj in objects)
        objects_with_relationships = sum(1 for obj in objects if obj.relationships)
        
        # Find oldest and newest
        oldest = min(objects, key=lambda x: x.first_seen)
        newest = max(objects, key=lambda x: x.first_seen)
        
        return {
            "total_objects": len(objects),
            "total_relationships": total_relationships,
            "avg_relationships_per_object": total_relationships / len(objects),
            "objects_with_relationships": objects_with_relationships,
            "oldest_object": {
                "name": oldest.name,
                "first_seen": oldest.first_seen.isoformat()
            },
            "newest_object": {
                "name": newest.name, 
                "first_seen": newest.first_seen.isoformat()
            }
        }
    
    def replace_object(self, old_name: str, new_object: NarrativeObject) -> Dict[str, Any]:
        """
        Replace a specific object with a corrected version.
        
        Args:
            old_name: Name of the object to replace
            new_object: New object to replace it with
            
        Returns:
            Result dictionary with success status and stats
        """
        # Check if old object exists
        if old_name not in self.collection.objects:
            return {
                "success": False,
                "error": f"Object '{old_name}' not found",
                "objects": list(self.collection.objects.values()),
                "total_count": len(self.collection.objects),
                "stats": {"added": 0, "updated": 0, "unchanged": 0, "removed": 0}
            }
        
        # Remove old object and add new one
        self.collection.remove(old_name)
        self.collection.add_or_update(new_object)
        
        # Save if needed
        if self.save_file:
            self.save_to_file(self.save_file)
        
        return {
            "success": True,
            "objects": list(self.collection.objects.values()),
            "total_count": len(self.collection.objects),
            "stats": {"added": 0, "updated": 1, "unchanged": 0, "removed": 0},
            "error": None
        }