#!/usr/bin/env python3
"""
Test suite for models and object merging logic.
"""
from datetime import datetime, timedelta
from models import NarrativeObject, Relationship, ObjectCollection
from object_manager import ObjectManager
import tempfile
import os


def test_narrative_object_basics():
    """Test basic NarrativeObject functionality."""
    print("Testing NarrativeObject basics...")
    
    # Create objects
    rel1 = Relationship("Bob", "Alice's friend")
    obj1 = NarrativeObject("Alice", "A young woman", [rel1])
    obj2 = NarrativeObject("Alice", "A young woman", [rel1])
    
    # Test equality (based on name)
    assert obj1 == obj2, "Objects with same name should be equal"
    
    # Test hashing (for use in sets)
    obj_set = {obj1, obj2}
    assert len(obj_set) == 1, "Objects with same name should hash to same value"
    
    print("✓ Basic functionality works")


def test_object_updates():
    """Test object update functionality."""
    print("Testing object updates...")
    
    # Original object
    rel1 = Relationship("Bob", "Alice's friend")
    obj1 = NarrativeObject("Alice", "A young woman", [rel1])
    original_time = obj1.last_updated
    
    # Wait a tiny bit to ensure time difference
    import time
    time.sleep(0.01)
    
    # Updated object with different description
    rel2 = Relationship("Carol", "Alice's sister")
    obj2 = NarrativeObject("Alice", "A brilliant scientist", [rel2])
    
    # Test update
    changed = obj1.update_from(obj2)
    assert changed, "Update should return True when changes made"
    assert obj1.description == "A brilliant scientist", "Description should be updated"
    assert len(obj1.relationships) == 1, "Should have one relationship"
    assert obj1.relationships[0].target == "Carol", "Relationship should be updated"
    assert obj1.last_updated > original_time, "Last updated time should change"
    
    # Test no change update
    obj3 = NarrativeObject("Alice", "A brilliant scientist", [rel2])
    changed = obj1.update_from(obj3)
    assert not changed, "Update should return False when no changes"
    
    print("✓ Object updates work correctly")


def test_object_collection():
    """Test ObjectCollection functionality."""
    print("Testing ObjectCollection...")
    
    collection = ObjectCollection()
    
    # Add objects
    obj1 = NarrativeObject("Alice", "A scientist")
    obj2 = NarrativeObject("Bob", "A teacher")
    
    result1 = collection.add_or_update(obj1)
    result2 = collection.add_or_update(obj2)
    
    assert result1, "Adding new object should return True"
    assert result2, "Adding new object should return True"
    assert len(collection.objects) == 2, "Collection should have 2 objects"
    
    # Update existing object
    obj1_updated = NarrativeObject("Alice", "A brilliant scientist")
    result3 = collection.add_or_update(obj1_updated)
    
    assert result3, "Updating object should return True"
    assert len(collection.objects) == 2, "Collection should still have 2 objects"
    assert collection.get("Alice").description == "A brilliant scientist"
    
    # Test removal
    removed = collection.remove("Bob")
    assert removed, "Removing existing object should return True"
    assert len(collection.objects) == 1, "Collection should have 1 object"
    
    removed = collection.remove("NonExistent")
    assert not removed, "Removing non-existent object should return False"
    
    print("✓ ObjectCollection works correctly")


def test_merge_scenarios():
    """Test various merge scenarios."""
    print("Testing merge scenarios...")
    
    collection = ObjectCollection()
    
    # Initial objects
    initial_objects = [
        NarrativeObject("Alice", "A scientist"),
        NarrativeObject("Bob", "A teacher"),
        NarrativeObject("Carol", "A doctor")
    ]
    
    stats1 = collection.merge_from_list(initial_objects)
    assert stats1["added"] == 3, f"Should add 3 objects, got {stats1}"
    assert stats1["updated"] == 0, f"Should update 0 objects, got {stats1}"
    assert stats1["removed"] == 0, f"Should remove 0 objects, got {stats1}"
    
    # Update scenario: modify existing objects, add new one, remove one
    updated_objects = [
        NarrativeObject("Alice", "A brilliant scientist"),  # updated
        NarrativeObject("Bob", "A teacher"),  # unchanged
        NarrativeObject("David", "An engineer")  # new (Carol removed)
    ]
    
    stats2 = collection.merge_from_list(updated_objects)
    assert stats2["added"] == 1, f"Should add 1 object, got {stats2}"
    assert stats2["updated"] == 1, f"Should update 1 object, got {stats2}"
    assert stats2["unchanged"] == 1, f"Should have 1 unchanged, got {stats2}"
    assert stats2["removed"] == 1, f"Should remove 1 object, got {stats2}"
    
    # Verify final state
    final_objects = collection.list_all()
    names = {obj.name for obj in final_objects}
    assert names == {"Alice", "Bob", "David"}, f"Final objects should be Alice, Bob, David, got {names}"
    assert collection.get("Alice").description == "A brilliant scientist"
    
    print("✓ Merge scenarios work correctly")


def test_serialization():
    """Test object serialization/deserialization."""
    print("Testing serialization...")
    
    # Create collection with objects
    rel1 = Relationship("Bob", "Alice's friend")
    obj1 = NarrativeObject("Alice", "A scientist", [rel1])
    obj2 = NarrativeObject("Bob", "A teacher")
    
    collection = ObjectCollection()
    collection.add_or_update(obj1)
    collection.add_or_update(obj2)
    
    # Serialize
    data = collection.to_dict()
    assert "objects" in data
    assert "count" in data
    assert data["count"] == 2
    
    # Deserialize
    new_collection = ObjectCollection.from_dict(data)
    assert len(new_collection.objects) == 2
    
    alice = new_collection.get("Alice")
    assert alice is not None
    assert alice.description == "A scientist"
    assert len(alice.relationships) == 1
    assert alice.relationships[0].target == "Bob"
    
    print("✓ Serialization works correctly")


def test_object_manager():
    """Test ObjectManager functionality."""
    print("Testing ObjectManager...")
    
    # Create temporary file for testing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_file = f.name
    
    try:
        # Test manager with persistence
        manager = ObjectManager(save_file=temp_file)
        
        # Simulate LLM response
        llm_response = '''
        {
          "objects": [
            {
              "name": "Alice",
              "description": "A scientist working on AI",
              "relationships": []
            },
            {
              "name": "Bob", 
              "description": "Alice's research partner",
              "relationships": [
                {
                  "target": "Alice",
                  "description": "Works closely with Alice on AI research"
                }
              ]
            }
          ]
        }
        '''
        
        # Process update
        result = manager.process_text_update("Some text", llm_response)
        
        assert result["success"], f"Processing should succeed, got {result}"
        assert result["stats"]["added"] == 2, "Should add 2 objects"
        assert result["total_count"] == 2, "Should have 2 total objects"
        
        # Test persistence by creating new manager
        manager2 = ObjectManager(save_file=temp_file)
        assert manager2.get_object_count() == 2, "Should load 2 objects from file"
        
        # Test statistics
        stats = manager2.get_statistics()
        assert stats["total_objects"] == 2
        assert stats["total_relationships"] == 1
        
        # Test summary
        summary = manager2.get_objects_summary()
        assert summary["total_count"] == 2
        assert len(summary["objects"]) == 2
        
        print("✓ ObjectManager works correctly")
        
    finally:
        # Clean up
        if os.path.exists(temp_file):
            os.unlink(temp_file)


def test_error_handling():
    """Test error handling in various scenarios."""
    print("Testing error handling...")
    
    manager = ObjectManager()
    
    # Test malformed JSON
    result = manager.process_text_update("text", "invalid json")
    assert result["success"], "Should handle invalid JSON gracefully"
    assert result["total_count"] == 0, "Should have no objects after invalid JSON"
    
    # Test empty response
    result = manager.process_text_update("text", "")
    assert result["success"], "Should handle empty response gracefully"
    assert result["total_count"] == 0, "Should have no objects"
    
    print("✓ Error handling works correctly")


def main():
    """Run all model tests."""
    print("=== Testing Models and Object Management ===")
    
    test_narrative_object_basics()
    test_object_updates()
    test_object_collection()
    test_merge_scenarios()
    test_serialization()
    test_object_manager()
    test_error_handling()
    
    print("\n✓ All model tests passed!")


if __name__ == "__main__":
    main()