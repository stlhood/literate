#!/usr/bin/env python3
"""
Test script to verify OpenAI integration fix.
"""
import os
from llm_client import LLMClient

def test_openai_client_creation():
    """Test that OpenAI client can be created without attribute errors."""
    print("Testing OpenAI client creation...")
    
    # Check if API key is available
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠ OPENAI_API_KEY not found - testing with dummy key")
        os.environ["OPENAI_API_KEY"] = "dummy-key-for-testing"
    
    try:
        client = LLMClient(provider="openai")
        print("✓ OpenAI client created successfully")
        
        # Check that all required attributes exist
        attrs = ["provider", "model", "temperature", "timeout", "base_url", "api_key"]
        for attr in attrs:
            if hasattr(client, attr):
                value = getattr(client, attr)
                print(f"✓ Attribute '{attr}': {value}")
            else:
                print(f"✗ Missing attribute '{attr}'")
                return False
        
        return True
        
    except ValueError as e:
        if "OPENAI_API_KEY not found" in str(e):
            print(f"✓ Properly validates API key requirement: {e}")
            return True
        else:
            print(f"✗ Unexpected ValueError: {e}")
            return False
    except Exception as e:
        print(f"✗ OpenAI client creation failed: {e}")
        return False
    finally:
        # Clean up dummy key if we set it
        if not api_key:
            del os.environ["OPENAI_API_KEY"]

def test_ollama_client_still_works():
    """Test that Ollama client still works after changes."""
    print("\nTesting Ollama client (should still work)...")
    
    try:
        client = LLMClient(provider="ollama")
        print("✓ Ollama client created successfully")
        
        # Check base_url is properly set for Ollama
        if client.base_url == "http://localhost:11434":
            print("✓ Ollama base_url set correctly")
        else:
            print(f"✗ Ollama base_url incorrect: {client.base_url}")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Ollama client creation failed: {e}")
        return False

def test_provider_differentiation():
    """Test that both providers have correct attributes."""
    print("\nTesting provider differentiation...")
    
    # Set dummy key for OpenAI test
    os.environ["OPENAI_API_KEY"] = "dummy-key"
    
    try:
        ollama_client = LLMClient(provider="ollama")
        openai_client = LLMClient(provider="openai")
        
        # Check provider types
        if ollama_client.provider == "ollama":
            print("✓ Ollama client has correct provider")
        else:
            print("✗ Ollama client has wrong provider")
            return False
        
        if openai_client.provider == "openai":
            print("✓ OpenAI client has correct provider")
        else:
            print("✗ OpenAI client has wrong provider")
            return False
        
        # Check base_url handling
        if ollama_client.base_url == "http://localhost:11434":
            print("✓ Ollama has correct base_url")
        else:
            print("✗ Ollama has wrong base_url")
            return False
        
        if openai_client.base_url is None:
            print("✓ OpenAI has base_url set to None (correct)")
        else:
            print(f"✗ OpenAI has unexpected base_url: {openai_client.base_url}")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Provider differentiation test failed: {e}")
        return False
    finally:
        # Clean up
        del os.environ["OPENAI_API_KEY"]

def main():
    """Run all tests."""
    print("Testing OpenAI integration fix...\n")
    
    tests = [
        test_openai_client_creation,
        test_ollama_client_still_works,
        test_provider_differentiation
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
    
    print(f"\nResults: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("✓ OpenAI integration fix is working!")
        print("✓ Both OpenAI and Ollama clients can be created without attribute errors.")
        return True
    else:
        print("✗ OpenAI integration fix needs more work.")
        return False

if __name__ == "__main__":
    success = main()
    import sys
    sys.exit(0 if success else 1)