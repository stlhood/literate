#!/usr/bin/env python3
"""
Test LLM with more complex text scenarios.
"""
from llm_client import LLMClient

def test_relationships():
    """Test extraction with relationships."""
    print("Testing relationship extraction...")
    client = LLMClient()
    
    complex_text = """
    In the bustling city of Paris, Detective Sarah investigated the mysterious disappearance 
    of Professor Johnson. She discovered that Johnson had been researching ancient artifacts 
    at the Louvre Museum before he vanished. Sarah's partner, Detective Mike, found evidence 
    that Johnson had been in contact with a suspicious antiquities dealer named Vincent.
    """
    
    try:
        objects = client.extract_narrative_objects(complex_text)
        print(f"Extracted {len(objects)} objects:")
        
        for obj in objects:
            print(f"\n- {obj.name}: {obj.description}")
            if obj.relationships:
                for rel in obj.relationships:
                    print(f"  → {rel.target}: {rel.description}")
            else:
                print("  (no relationships)")
        
        return len(objects) > 0
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_edge_cases():
    """Test various edge cases."""
    client = LLMClient()
    
    print("\nTesting edge cases...")
    
    # Technical text (should extract few objects)
    tech_text = "The function calculates the derivative using the chain rule algorithm."
    objects = client.extract_narrative_objects(tech_text)
    print(f"Technical text: {len(objects)} objects")
    
    # Single word
    objects = client.extract_narrative_objects("Hello")
    print(f"Single word: {len(objects)} objects")
    
    # Very long text
    long_text = "Alice " * 100 + "met Bob."
    objects = client.extract_narrative_objects(long_text)
    print(f"Long text: {len(objects)} objects")

def main():
    print("=== Complex LLM Tests ===")
    
    success = test_relationships()
    if success:
        test_edge_cases()
        print("\n✓ All complex tests completed")
    else:
        print("\n✗ Relationship test failed")

if __name__ == "__main__":
    main()