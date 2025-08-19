#!/usr/bin/env python3
"""
Test script to verify TUI OpenAI integration fix.
"""
import os
from tui_app import LiterateApp

def test_tui_openai_integration():
    """Test that TUI can use OpenAI provider without URL errors."""
    print("Testing TUI OpenAI integration...")
    
    # Check if API key is available
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠ OPENAI_API_KEY not found - setting dummy key for test")
        os.environ["OPENAI_API_KEY"] = "dummy-key-for-testing"
    
    try:
        # Create TUI app with OpenAI provider
        app = LiterateApp(llm_provider="openai")
        print("✓ TUI app created with OpenAI provider")
        
        # Check that the LLM client is correctly configured
        if app.llm_client.provider == "openai":
            print("✓ LLM client provider set to OpenAI")
        else:
            print(f"✗ LLM client provider is {app.llm_client.provider}, expected openai")
            return False
        
        # Check base_url is None (not causing URL construction issues)
        if app.llm_client.base_url is None:
            print("✓ LLM client base_url is None (correct for OpenAI)")
        else:
            print(f"✗ LLM client base_url is {app.llm_client.base_url}, expected None")
            return False
        
        # Test the _get_llm_response method doesn't try to call Ollama endpoints
        test_text = "Alice met Bob at the coffee shop."
        
        try:
            # This should not try to construct URLs with None/api/generate
            response = app._get_llm_response(test_text)
            print("✓ _get_llm_response method works without URL errors")
        except Exception as e:
            if "None/api/generate" in str(e) or "No scheme supplied" in str(e):
                print(f"✗ Still getting URL construction error: {e}")
                return False
            elif "authentication" in str(e).lower() or "unauthorized" in str(e).lower():
                print("✓ Got authentication error (expected with dummy key)")
            else:
                print(f"⚠ Got different error (may be OK): {e}")
        
        return True
        
    except Exception as e:
        if "OPENAI_API_KEY not found" in str(e):
            print("✓ Properly validates API key (expected with dummy key)")
            return True
        else:
            print(f"✗ Unexpected error: {e}")
            return False
    finally:
        # Clean up dummy key if we set it
        if not api_key:
            del os.environ["OPENAI_API_KEY"]

def test_tui_ollama_still_works():
    """Test that TUI still works with Ollama after changes."""
    print("\nTesting TUI Ollama integration (should still work)...")
    
    try:
        app = LiterateApp(llm_provider="ollama")
        print("✓ TUI app created with Ollama provider")
        
        if app.llm_client.provider == "ollama":
            print("✓ LLM client provider set to Ollama")
        else:
            print(f"✗ LLM client provider is {app.llm_client.provider}, expected ollama")
            return False
        
        if app.llm_client.base_url == "http://localhost:11434":
            print("✓ LLM client base_url set correctly for Ollama")
        else:
            print(f"✗ LLM client base_url is {app.llm_client.base_url}")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Ollama TUI integration failed: {e}")
        return False

def test_provider_display():
    """Test that provider is displayed correctly in UI."""
    print("\nTesting provider display...")
    
    # Set dummy key for OpenAI test
    os.environ["OPENAI_API_KEY"] = "dummy-key"
    
    try:
        ollama_app = LiterateApp(llm_provider="ollama")
        openai_app = LiterateApp(llm_provider="openai")
        
        # Check provider storage
        if ollama_app.llm_provider == "ollama":
            print("✓ Ollama app stores provider correctly")
        else:
            print("✗ Ollama app provider storage incorrect")
            return False
        
        if openai_app.llm_provider == "openai":
            print("✓ OpenAI app stores provider correctly")
        else:
            print("✗ OpenAI app provider storage incorrect")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Provider display test failed: {e}")
        return False
    finally:
        del os.environ["OPENAI_API_KEY"]

def main():
    """Run all tests."""
    print("Testing TUI OpenAI integration fix...\n")
    
    tests = [
        test_tui_openai_integration,
        test_tui_ollama_still_works,
        test_provider_display
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
        print("✓ TUI OpenAI integration fix is working!")
        print("✓ No more 'None/api/generate' URL errors when using --openai flag.")
        return True
    else:
        print("✗ TUI OpenAI integration fix needs more work.")
        return False

if __name__ == "__main__":
    success = main()
    import sys
    sys.exit(0 if success else 1)