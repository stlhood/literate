#!/usr/bin/env python3
"""
Test comprehensive error handling scenarios.
"""
from object_manager import ObjectManager


def test_malformed_responses():
    """Test various malformed response scenarios."""
    print("Testing malformed responses...")
    
    manager = ObjectManager()
    
    test_cases = [
        # Completely invalid JSON
        ("invalid json", "Should handle completely invalid JSON"),
        
        # Valid JSON but wrong structure
        ('{"wrong": "structure"}', "Should handle wrong JSON structure"),
        
        # Missing required fields
        ('{"objects": [{"name": "Alice"}]}', "Should handle missing description"),
        
        # Empty objects array
        ('{"objects": []}', "Should handle empty objects array"),
        
        # Null values
        ('{"objects": [{"name": null, "description": "test"}]}', "Should handle null name"),
        
        # Very long strings
        ('{"objects": [{"name": "Alice", "description": "' + "A" * 1000 + '"}]}', "Should handle very long description"),
        
        # Invalid relationship structure
        ('{"objects": [{"name": "Alice", "description": "test", "relationships": [{"target": "Bob"}]}]}', "Should handle missing relationship description"),
        
        # Circular/self relationships
        ('{"objects": [{"name": "Alice", "description": "test", "relationships": [{"target": "Alice", "description": "knows herself"}]}]}', "Should handle self-relationships"),
        
        # Unicode and special characters
        ('{"objects": [{"name": "Alicé 🤖", "description": "A person with émojis"}]}', "Should handle unicode"),
        
        # Mixed valid/invalid objects
        ('{"objects": [{"name": "Alice", "description": "valid"}, {"invalid": "object"}]}', "Should handle mixed valid/invalid objects")
    ]
    
    for response, description in test_cases:
        result = manager.process_text_update("test", response)
        print(f"  {description}: {'✓' if result['success'] else '✗'}")
        
        # All should succeed gracefully (even if returning empty results)
        assert result["success"], f"Failed handling: {description}"
    
    print("✓ All malformed response scenarios handled gracefully")


def test_edge_case_merging():
    """Test edge cases in object merging."""
    print("Testing edge case merging...")
    
    manager = ObjectManager()
    
    # Start with some objects
    response1 = '''
    {
      "objects": [
        {"name": "Alice", "description": "A scientist"},
        {"name": "Bob", "description": "A teacher"}
      ]
    }
    '''
    
    result1 = manager.process_text_update("text1", response1)
    assert result1["stats"]["added"] == 2
    
    # Now test various merge scenarios
    
    # Complete replacement
    response2 = '''
    {
      "objects": [
        {"name": "Carol", "description": "A doctor"},
        {"name": "David", "description": "An engineer"}
      ]
    }
    '''
    
    result2 = manager.process_text_update("text2", response2)
    assert result2["stats"]["added"] == 2, "Should add 2 new objects"
    assert result2["stats"]["removed"] == 2, "Should remove 2 old objects"
    
    # Empty response (should clear all)
    response3 = '{"objects": []}'
    result3 = manager.process_text_update("text3", response3)
    assert result3["stats"]["removed"] == 2, "Should remove all objects"
    assert result3["total_count"] == 0, "Should have no objects"
    
    # Add back and test duplicate names with different cases
    response4 = '''
    {
      "objects": [
        {"name": "alice", "description": "lowercase alice"},
        {"name": "Alice", "description": "uppercase Alice"}
      ]
    }
    '''
    
    result4 = manager.process_text_update("text4", response4)
    # Should treat these as different objects (case sensitive)
    assert result4["total_count"] == 2, "Should treat different cases as different objects"
    
    print("✓ Edge case merging handled correctly")


def test_relationship_validation():
    """Test relationship validation edge cases."""
    print("Testing relationship validation...")
    
    manager = ObjectManager()
    
    # Response with invalid relationship targets
    response = '''
    {
      "objects": [
        {
          "name": "Alice",
          "description": "A scientist",
          "relationships": [
            {"target": "Bob", "description": "friends with Bob"},
            {"target": "NonExistent", "description": "knows someone who doesn't exist"}
          ]
        },
        {
          "name": "Bob",
          "description": "A teacher",
          "relationships": []
        }
      ]
    }
    '''
    
    result = manager.process_text_update("text", response)
    assert result["success"], "Should handle invalid relationships"
    
    # Check that invalid relationship was removed
    alice = manager.get_object("Alice")
    assert alice is not None, "Alice should exist"
    assert len(alice.relationships) == 1, "Should have only 1 valid relationship"
    assert alice.relationships[0].target == "Bob", "Should keep valid relationship to Bob"
    
    print("✓ Relationship validation works correctly")


def main():
    """Run all error handling tests."""
    print("=== Testing Comprehensive Error Handling ===")
    
    test_malformed_responses()
    test_edge_case_merging()
    test_relationship_validation()
    
    print("\n✓ All error handling tests passed!")


if __name__ == "__main__":
    main()