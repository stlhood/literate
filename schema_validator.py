"""
JSON schema validation for LLM responses.
"""
from typing import Dict, Any, List, Union, Optional
import json


class SchemaValidator:
    """Validates LLM responses against expected schema."""
    
    # Expected JSON schema for LLM responses
    EXPECTED_SCHEMA = {
        "type": "object",
        "required": ["objects"],
        "properties": {
            "objects": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["name", "description"],
                    "properties": {
                        "name": {
                            "type": "string",
                            "minLength": 1,
                            "maxLength": 100
                        },
                        "description": {
                            "type": "string",
                            "minLength": 1,
                            "maxLength": 500
                        },
                        "relationships": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": ["target", "description"],
                                "properties": {
                                    "target": {
                                        "type": "string",
                                        "minLength": 1,
                                        "maxLength": 100
                                    },
                                    "description": {
                                        "type": "string",
                                        "minLength": 1,
                                        "maxLength": 200
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    @classmethod
    def validate_response(cls, response_data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate LLM response data against expected schema.
        
        Args:
            response_data: Parsed JSON response from LLM
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check top-level structure
        if not isinstance(response_data, dict):
            errors.append("Response must be a JSON object")
            return False, errors
        
        if "objects" not in response_data:
            errors.append("Response missing required 'objects' field")
            return False, errors
        
        objects = response_data["objects"]
        if not isinstance(objects, list):
            errors.append("'objects' field must be an array")
            return False, errors
        
        # Validate each object
        for i, obj in enumerate(objects):
            obj_errors = cls._validate_object(obj, i)
            errors.extend(obj_errors)
        
        return len(errors) == 0, errors
    
    @classmethod
    def _validate_object(cls, obj: Any, index: int) -> List[str]:
        """Validate a single narrative object."""
        errors = []
        prefix = f"Object {index}: "
        
        if not isinstance(obj, dict):
            errors.append(f"{prefix}must be a JSON object")
            return errors
        
        # Check required fields
        if "name" not in obj:
            errors.append(f"{prefix}missing required 'name' field")
        elif not isinstance(obj["name"], str) or len(obj["name"].strip()) == 0:
            errors.append(f"{prefix}'name' must be a non-empty string")
        elif len(obj["name"]) > 100:
            errors.append(f"{prefix}'name' too long (max 100 characters)")
        
        if "description" not in obj:
            errors.append(f"{prefix}missing required 'description' field")
        elif not isinstance(obj["description"], str) or len(obj["description"].strip()) == 0:
            errors.append(f"{prefix}'description' must be a non-empty string")
        elif len(obj["description"]) > 500:
            errors.append(f"{prefix}'description' too long (max 500 characters)")
        
        # Check optional relationships field
        if "relationships" in obj:
            relationships = obj["relationships"]
            if not isinstance(relationships, list):
                errors.append(f"{prefix}'relationships' must be an array")
            else:
                for j, rel in enumerate(relationships):
                    rel_errors = cls._validate_relationship(rel, index, j)
                    errors.extend(rel_errors)
        
        return errors
    
    @classmethod
    def _validate_relationship(cls, rel: Any, obj_index: int, rel_index: int) -> List[str]:
        """Validate a single relationship."""
        errors = []
        prefix = f"Object {obj_index}, Relationship {rel_index}: "
        
        if not isinstance(rel, dict):
            errors.append(f"{prefix}must be a JSON object")
            return errors
        
        if "target" not in rel:
            errors.append(f"{prefix}missing required 'target' field")
        elif not isinstance(rel["target"], str) or len(rel["target"].strip()) == 0:
            errors.append(f"{prefix}'target' must be a non-empty string")
        elif len(rel["target"]) > 100:
            errors.append(f"{prefix}'target' too long (max 100 characters)")
        
        if "description" not in rel:
            errors.append(f"{prefix}missing required 'description' field")
        elif not isinstance(rel["description"], str) or len(rel["description"].strip()) == 0:
            errors.append(f"{prefix}'description' must be a non-empty string")
        elif len(rel["description"]) > 200:
            errors.append(f"{prefix}'description' too long (max 200 characters)")
        
        return errors
    
    @classmethod
    def sanitize_response(cls, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize response data by fixing common issues.
        
        Args:
            response_data: Raw response data
            
        Returns:
            Sanitized response data
        """
        if not isinstance(response_data, dict):
            return {"objects": []}
        
        if "objects" not in response_data:
            return {"objects": []}
        
        objects = response_data["objects"]
        if not isinstance(objects, list):
            return {"objects": []}
        
        sanitized_objects = []
        for obj in objects:
            sanitized_obj = cls._sanitize_object(obj)
            if sanitized_obj:
                sanitized_objects.append(sanitized_obj)
        
        return {"objects": sanitized_objects}
    
    @classmethod
    def _sanitize_object(cls, obj: Any) -> Optional[Dict[str, Any]]:
        """Sanitize a single object, return None if invalid."""
        if not isinstance(obj, dict):
            return None
        
        # Extract and validate name
        name = obj.get("name")
        if name is None or not isinstance(name, str):
            return None
        name = name.strip()
        if not name or len(name) > 100:
            return None
        
        # Extract and validate description
        description = obj.get("description")
        if description is None or not isinstance(description, str):
            description = f"A {name.lower()} mentioned in the text."
        else:
            description = description.strip()
            if not description:
                description = f"A {name.lower()} mentioned in the text."
        if len(description) > 500:
            description = description[:497] + "..."
        
        # Extract and sanitize relationships
        relationships = []
        if "relationships" in obj and isinstance(obj["relationships"], list):
            for rel in obj["relationships"]:
                sanitized_rel = cls._sanitize_relationship(rel)
                if sanitized_rel:
                    relationships.append(sanitized_rel)
        
        return {
            "name": name,
            "description": description,
            "relationships": relationships
        }
    
    @classmethod
    def _sanitize_relationship(cls, rel: Any) -> Optional[Dict[str, str]]:
        """Sanitize a single relationship, return None if invalid."""
        if not isinstance(rel, dict):
            return None
        
        target = rel.get("target", "").strip()
        if not target or len(target) > 100:
            return None
        
        description = rel.get("description", "").strip()
        if not description:
            return None
        if len(description) > 200:
            description = description[:197] + "..."
        
        return {
            "target": target,
            "description": description
        }