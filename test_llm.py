#!/usr/bin/env python3
"""
Test script for LLM connectivity and response parsing.
"""
from llm_client import LLMClient

def test_connection():
    """Test basic connectivity to Ollama server."""
    print("Testing Ollama server connection...")
    client = LLMClient()
    
    if client.test_connection():
        print("✓ Successfully connected to Ollama server")
        return True
    else:
        print("✗ Failed to connect to Ollama server")
        print("  Make sure Ollama is running at localhost:11434")
        return False

def test_model_response():
    """Test model response with sample text."""
    print("\nTesting gemma2:270m model response...")
    client = LLMClient()
    
    # Simple test text
    test_text = "Alice met Bob at the coffee shop. They discussed their upcoming trip to Paris."
    
    try:
        objects = client.extract_narrative_objects(test_text)
        print(f"✓ Successfully extracted {len(objects)} objects:")
        
        for obj in objects:
            print(f"  - {obj.name}: {obj.description}")
            for rel in obj.relationships:
                print(f"    → {rel.target}: {rel.description}")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to extract objects: {e}")
        return False

def test_error_handling():
    """Test error handling with various scenarios."""
    print("\nTesting error handling...")
    
    # Test with invalid server
    print("  Testing invalid server URL...")
    client = LLMClient(base_url="http://localhost:99999")
    try:
        client.extract_narrative_objects("test")
        print("  ✗ Should have raised ConnectionError")
    except ConnectionError:
        print("  ✓ Correctly handled invalid server")
    except Exception as e:
        print(f"  ? Unexpected error: {e}")
    
    # Test with empty text
    print("  Testing empty text input...")
    client = LLMClient()
    try:
        objects = client.extract_narrative_objects("")
        if len(objects) == 0:
            print("  ✓ Correctly handled empty text")
        else:
            print("  ? Unexpected objects from empty text")
    except Exception as e:
        print(f"  ✗ Error with empty text: {e}")

def main():
    """Run all LLM tests."""
    print("=== LLM Integration Tests ===")
    
    # Test connection first
    if not test_connection():
        print("\nSkipping further tests - no connection to Ollama")
        return False
    
    # Test model response
    if not test_model_response():
        print("\nModel response test failed")
        return False
    
    # Test error handling
    test_error_handling()
    
    print("\n=== All tests completed ===")
    return True

if __name__ == "__main__":
    main()