#!/usr/bin/env python3
"""
Test script for incremental object preservation behavior.
"""
from models import NarrativeObject, Relationship, ObjectCollection
from object_manager import ObjectManager
import json

def create_mock_llm_response(objects_data):
    """Create a mock LLM response in the expected JSON format."""
    return json.dumps({
        "objects": [
            {
                "name": obj["name"],
                "description": obj["description"], 
                "relationships": obj.get("relationships", [])
            }
            for obj in objects_data
        ]
    })

def test_incremental_preservation():
    """Test that existing objects are preserved when new text is added."""
    print("Testing incremental object preservation...")
    
    # Create object manager
    manager = ObjectManager()
    
    # Step 1: Process initial text with some objects
    print("\n1. Adding initial objects...")
    initial_objects = [
        {"name": "Alice", "description": "A young woman who works at a bookstore"},
        {"name": "Bob", "description": "Alice's friend who loves coffee"}
    ]
    
    llm_response1 = create_mock_llm_response(initial_objects)
    result1 = manager.process_text_update("Alice works at a bookstore. Bob is her friend.", llm_response1)
    
    print(f"   Added {result1['stats']['added']} objects")
    print(f"   Total objects: {result1['total_count']}")
    for obj in result1['objects']:
        print(f"   - {obj.name}: {obj.description}")
    
    # Step 2: Add new text that introduces new objects but doesn't mention existing ones
    print("\n2. Adding new objects without mentioning existing ones...")
    new_objects = [
        {"name": "Charlie", "description": "A regular customer at the bookstore"},
        {"name": "Downtown Cafe", "description": "A cozy coffee shop on Main Street"}
    ]
    
    llm_response2 = create_mock_llm_response(new_objects)
    result2 = manager.process_text_update("Charlie comes in every day. There's a cafe downtown.", llm_response2)
    
    print(f"   Added {result2['stats']['added']} objects")
    print(f"   Updated {result2['stats']['updated']} objects")
    print(f"   Removed {result2['stats']['removed']} objects")
    print(f"   Total objects: {result2['total_count']}")
    
    print("   Current objects:")
    for obj in result2['objects']:
        print(f"   - {obj.name}: {obj.description}")
    
    # Verify that Alice and Bob are still there
    object_names = [obj.name for obj in result2['objects']]
    
    if "Alice" in object_names and "Bob" in object_names:
        print("   ✓ SUCCESS: Existing objects (Alice, Bob) were preserved!")
    else:
        print("   ✗ FAILED: Existing objects were removed!")
        return False
    
    if "Charlie" in object_names and "Downtown Cafe" in object_names:
        print("   ✓ SUCCESS: New objects (Charlie, Downtown Cafe) were added!")
    else:
        print("   ✗ FAILED: New objects were not added!")
        return False
    
    return True

def test_object_updates():
    """Test that existing objects can be updated when mentioned again."""
    print("\n\nTesting object updates...")
    
    manager = ObjectManager()
    
    # Add initial object
    initial_objects = [
        {"name": "Alice", "description": "A person"}
    ]
    
    llm_response1 = create_mock_llm_response(initial_objects)
    result1 = manager.process_text_update("Alice is a person.", llm_response1)
    
    print(f"   Initial: Alice - {result1['objects'][0].description}")
    
    # Update the same object with more detail
    updated_objects = [
        {"name": "Alice", "description": "A young woman who works at a bookstore and loves reading"}
    ]
    
    llm_response2 = create_mock_llm_response(updated_objects)
    result2 = manager.process_text_update("Alice works at a bookstore and loves reading.", llm_response2)
    
    print(f"   Updated: Alice - {result2['objects'][0].description}")
    print(f"   Stats: {result2['stats']['updated']} updated, {result2['stats']['added']} added")
    
    if result2['stats']['updated'] == 1 and result2['stats']['added'] == 0:
        print("   ✓ SUCCESS: Object was updated correctly!")
        return True
    else:
        print("   ✗ FAILED: Object update statistics incorrect!")
        return False

def test_explicit_removal():
    """Test that objects can still be explicitly removed when needed."""
    print("\n\nTesting explicit removal mode...")
    
    manager = ObjectManager()
    
    # Add some objects
    initial_objects = [
        {"name": "Alice", "description": "A person"},
        {"name": "Bob", "description": "Another person"}
    ]
    
    llm_response1 = create_mock_llm_response(initial_objects)
    result1 = manager.process_text_update("Alice and Bob are here.", llm_response1)
    
    print(f"   Initial objects: {[obj.name for obj in result1['objects']]}")
    
    # Process with only Alice, but with preserve_existing=False
    only_alice = [
        {"name": "Alice", "description": "A person"}
    ]
    
    llm_response2 = create_mock_llm_response(only_alice)
    result2 = manager.process_text_update("Only Alice is here now.", llm_response2, preserve_existing=False)
    
    object_names = [obj.name for obj in result2['objects']]
    print(f"   After removal: {object_names}")
    print(f"   Stats: {result2['stats']['removed']} removed")
    
    if "Alice" in object_names and "Bob" not in object_names:
        print("   ✓ SUCCESS: Explicit removal worked correctly!")
        return True
    else:
        print("   ✗ FAILED: Explicit removal didn't work!")
        return False

def main():
    """Run all tests."""
    print("Testing object preservation and merging behavior...\n")
    
    tests = [
        test_incremental_preservation,
        test_object_updates,
        test_explicit_removal
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"   ✗ Test failed with exception: {e}")
    
    print(f"\n\nResults: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("✓ All tests passed! Object preservation is working correctly.")
        print("✓ Existing narrative objects will now be preserved when new text is added.")
        return True
    else:
        print("✗ Some tests failed - object preservation needs more work.")
        return False

if __name__ == "__main__":
    success = main()
    import sys
    sys.exit(0 if success else 1)