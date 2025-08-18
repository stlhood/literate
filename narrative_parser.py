"""
Parser for converting LLM responses to narrative objects.
"""
import json
from typing import List, Dict, Any
from models import NarrativeObject, Relationship
from schema_validator import SchemaValidator


class NarrativeParser:
    """Parses LLM responses into NarrativeObject instances."""
    
    def __init__(self):
        self.validator = SchemaValidator()
    
    def parse_llm_response(self, response_text: str) -> List[NarrativeObject]:
        """
        Parse LLM response text into NarrativeObject instances.
        
        Args:
            response_text: Raw response text from LLM
            
        Returns:
            List of NarrativeObject instances
            
        Raises:
            ValueError: If response cannot be parsed or validated
        """
        if not response_text.strip():
            return []
        
        # Clean up markdown formatting
        cleaned_text = self._clean_response_text(response_text)
        
        # Check for placeholder responses that should be rejected entirely
        if self._is_placeholder_response(cleaned_text):
            print("Detected placeholder response, returning empty list")
            return []
        
        # Parse JSON
        try:
            response_data = json.loads(cleaned_text)
        except json.JSONDecodeError as e:
            # Try to salvage what we can
            print(f"JSON parsing failed, attempting salvage: {e}")
            return self._attempt_salvage_parse(cleaned_text)
        
        # Validate and sanitize
        is_valid, errors = self.validator.validate_response(response_data)
        if not is_valid:
            print(f"Schema validation failed: {errors}")
            # Attempt to sanitize
            response_data = self.validator.sanitize_response(response_data)
        
        # Convert to NarrativeObjects
        objects = self._convert_to_objects(response_data)
        
        # Final filter for quality
        return self._filter_quality_objects(objects)
    
    def _clean_response_text(self, response_text: str) -> str:
        """Clean up response text by removing markdown formatting."""
        text = response_text.strip()
        
        # Remove markdown code blocks
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        
        if text.endswith("```"):
            text = text[:-3]
        
        return text.strip()
    
    def _attempt_salvage_parse(self, text: str) -> List[NarrativeObject]:
        """
        Attempt to salvage parseable content from malformed JSON.
        
        This is a fallback method for when the LLM returns broken JSON.
        """
        # Try to extract object names using simple pattern matching
        objects = []
        
        # Look for name patterns
        lines = text.split('\n')
        current_name = None
        current_description = None
        
        for line in lines:
            line = line.strip()
            
            # Look for name field
            if '"name"' in line and ':' in line:
                try:
                    # Extract value after colon
                    value_part = line.split(':', 1)[1].strip()
                    if value_part.startswith('"') and value_part.endswith('",'):
                        current_name = value_part[1:-2]  # Remove quotes and comma
                    elif value_part.startswith('"') and value_part.endswith('"'):
                        current_name = value_part[1:-1]  # Remove quotes
                except:
                    continue
            
            # Look for description field
            elif '"description"' in line and ':' in line and current_name:
                try:
                    value_part = line.split(':', 1)[1].strip()
                    if value_part.startswith('"') and (value_part.endswith('",') or value_part.endswith('"')):
                        current_description = value_part[1:].rstrip('",')
                        
                        # Create object
                        if current_name and current_description:
                            obj = NarrativeObject(
                                name=current_name,
                                description=current_description,
                                relationships=[]
                            )
                            objects.append(obj)
                            current_name = None
                            current_description = None
                except:
                    continue
        
        return objects
    
    def _convert_to_objects(self, response_data: Dict[str, Any]) -> List[NarrativeObject]:
        """Convert validated response data to NarrativeObject instances."""
        objects = []
        
        for obj_data in response_data.get("objects", []):
            # Parse relationships
            relationships = []
            for rel_data in obj_data.get("relationships", []):
                rel = Relationship(
                    target=rel_data["target"],
                    description=rel_data["description"]
                )
                relationships.append(rel)
            
            # Create narrative object
            obj = NarrativeObject(
                name=obj_data["name"],
                description=obj_data["description"],
                relationships=relationships
            )
            objects.append(obj)
        
        return objects
    
    def _is_placeholder_response(self, response_text: str) -> bool:
        """Check if response contains only placeholder content."""
        # Check for responses that are just the example format
        placeholder_indicators = [
            '"name": "string"',
            '"description": "string"',
            'ExactNameFromText',
            'Brief description based only on what the text says'
        ]
        
        for indicator in placeholder_indicators:
            if indicator in response_text:
                return True
        
        return False
    
    def _filter_quality_objects(self, objects: List[NarrativeObject]) -> List[NarrativeObject]:
        """Filter out low-quality objects."""
        quality_objects = []
        
        for obj in objects:
            # Skip objects with placeholder or generic content
            if (obj.name.lower() in ['string', 'name', 'object'] or 
                obj.description.lower() in ['string', 'description'] or
                len(obj.name.strip()) < 2 or
                len(obj.description.strip()) < 5):
                continue
                
            # Check for title case proper names (more likely to be real names)
            is_proper_name = (obj.name[0].isupper() and 
                             not obj.name.lower().startswith('the ') and
                             not obj.name.lower() in ['person', 'character', 'object'])
            
            # Keep objects that look like proper names or specific places/things
            if is_proper_name or any(word in obj.name.lower() for word in ['library', 'castle', 'park', 'school', 'book', 'sword', 'map']):
                quality_objects.append(obj)
        
        return quality_objects
    
    def validate_relationships(self, objects: List[NarrativeObject]) -> List[NarrativeObject]:
        """
        Validate that all relationship targets exist in the object list.
        Remove relationships to non-existent objects.
        
        Args:
            objects: List of NarrativeObjects
            
        Returns:
            List of NarrativeObjects with validated relationships
        """
        object_names = {obj.name for obj in objects}
        
        for obj in objects:
            valid_relationships = []
            for rel in obj.relationships:
                if rel.target in object_names:
                    valid_relationships.append(rel)
                else:
                    print(f"Removing invalid relationship: {obj.name} -> {rel.target}")
            obj.relationships = valid_relationships
        
        return objects