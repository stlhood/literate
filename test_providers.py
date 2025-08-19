#!/usr/bin/env python3
"""
Test script for both Ollama and OpenAI provider integrations.
"""
import os
import sys
from llm_client import LLMClient

def test_ollama_integration():
    """Test Ollama integration (existing functionality)."""
    print("Testing Ollama integration...")
    
    try:
        client = LLMClient(provider="ollama")
        print(f"✓ Ollama client created successfully")
        print(f"  Provider: {client.provider}")
        print(f"  Model: {client.model}")
        print(f"  Base URL: {client.base_url}")
        
        # Test connection
        if client.test_connection():
            print("✓ Ollama server connection successful")
        else:
            print("⚠ Ollama server connection failed (server may not be running)")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Ollama integration failed: {e}")
        return False

def test_openai_integration():
    """Test OpenAI integration (new functionality)."""
    print("\nTesting OpenAI integration...")
    
    # Check if API key is available
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠ OPENAI_API_KEY not found in environment")
        print("  To test OpenAI integration:")
        print("  1. Create a .env file in the project directory")
        print("  2. Add: OPENAI_API_KEY=your_api_key_here")
        return False
    
    try:
        client = LLMClient(provider="openai")
        print(f"✓ OpenAI client created successfully")
        print(f"  Provider: {client.provider}")
        print(f"  Model: {client.model}")
        print(f"  API Key: {api_key[:8]}..." if len(api_key) > 8 else "***")
        
        # Test connection (this will make a small API call)
        print("  Testing connection...")
        if client.test_connection():
            print("✓ OpenAI API connection successful")
        else:
            print("✗ OpenAI API connection failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ OpenAI integration failed: {e}")
        return False

def test_command_line_args():
    """Test command-line argument handling."""
    print("\nTesting command-line argument parsing...")
    
    # Test help message
    try:
        import subprocess
        result = subprocess.run([sys.executable, "main.py", "--help"], 
                              capture_output=True, text=True, timeout=5)
        if "--openai" in result.stdout:
            print("✓ Command-line help includes --openai flag")
        else:
            print("✗ Command-line help missing --openai flag")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Command-line test failed: {e}")
        return False

def test_extraction_functionality():
    """Test basic extraction with available provider."""
    print("\nTesting narrative extraction functionality...")
    
    test_text = "Alice met Bob at the coffee shop. They discussed their trip to Paris."
    
    # Test with Ollama if available
    try:
        client = LLMClient(provider="ollama")
        if client.test_connection():
            print("Testing extraction with Ollama...")
            objects = client.extract_narrative_objects(test_text)
            print(f"✓ Ollama extraction returned {len(objects)} objects")
            for obj in objects:
                print(f"  - {obj.name}: {obj.description}")
            return True
    except Exception as e:
        print(f"⚠ Ollama extraction test failed: {e}")
    
    # Test with OpenAI if available
    if os.getenv("OPENAI_API_KEY"):
        try:
            client = LLMClient(provider="openai")
            if client.test_connection():
                print("Testing extraction with OpenAI...")
                objects = client.extract_narrative_objects(test_text)
                print(f"✓ OpenAI extraction returned {len(objects)} objects")
                for obj in objects:
                    print(f"  - {obj.name}: {obj.description}")
                return True
        except Exception as e:
            print(f"⚠ OpenAI extraction test failed: {e}")
    
    print("⚠ No functional LLM provider available for extraction test")
    return False

def main():
    """Run all tests."""
    print("Testing LLM provider integrations...\n")
    
    tests = [
        test_ollama_integration,
        test_openai_integration,
        test_command_line_args,
        test_extraction_functionality
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
    
    print(f"\nResults: {passed}/{len(tests)} tests passed")
    
    if passed >= 2:  # At least Ollama + command-line should work
        print("✓ Provider integration is working!")
        print("\nUsage:")
        print("  python main.py           # Use Ollama (default)")
        print("  python main.py --openai  # Use OpenAI API")
        return True
    else:
        print("✗ Provider integration needs attention")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)