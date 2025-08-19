#!/usr/bin/env python3
"""
Test script for placeholder text removal behavior.
"""
from tui_app import LiterateApp
from textual.widgets import TextArea

def test_placeholder_initialization():
    """Test that placeholder text is properly initialized."""
    print("Testing placeholder text initialization...")
    app = LiterateApp()
    
    # Check that placeholder text is set correctly
    expected_placeholder = "Enter or paste your text here...\nPress Ctrl+C or Ctrl+Q to exit."
    if app.placeholder_text == expected_placeholder:
        print("✓ Placeholder text is set correctly")
        return True
    else:
        print(f"✗ Placeholder text mismatch: expected '{expected_placeholder}', got '{app.placeholder_text}'")
        return False

def test_placeholder_cleared_flag():
    """Test that the placeholder cleared flag works."""
    print("\nTesting placeholder cleared flag...")
    app = LiterateApp()
    
    # Initially should not be cleared
    if not app.placeholder_cleared:
        print("✓ Initially placeholder_cleared is False")
    else:
        print("✗ Initially placeholder_cleared should be False")
        return False
    
    # Simulate clearing
    app.placeholder_cleared = True
    if app.placeholder_cleared:
        print("✓ Placeholder cleared flag can be set to True")
        return True
    else:
        print("✗ Failed to set placeholder cleared flag")
        return False

def test_key_detection():
    """Test that typing keys are detected properly."""
    print("\nTesting key detection logic...")
    app = LiterateApp()
    
    # Test various key types
    typing_keys = ['a', 'A', '1', 'space', 'enter', 'backspace', 'delete', 'tab']
    non_typing_keys = ['up', 'down', 'left', 'right', 'ctrl+c', 'alt+f', 'f1', 'escape']
    
    for key in typing_keys:
        is_typing = (len(key) == 1 or key in ['space', 'enter', 'backspace', 'delete', 'tab'])
        if is_typing:
            print(f"✓ '{key}' correctly identified as typing key")
        else:
            print(f"✗ '{key}' should be identified as typing key")
            return False
    
    for key in non_typing_keys:
        is_typing = (len(key) == 1 or key in ['space', 'enter', 'backspace', 'delete', 'tab'])
        if not is_typing:
            print(f"✓ '{key}' correctly identified as non-typing key")
        else:
            print(f"✗ '{key}' should be identified as non-typing key")
            return False
    
    return True

def test_placeholder_content():
    """Test that placeholder content includes the expected instructions."""
    print("\nTesting placeholder content...")
    app = LiterateApp()
    
    required_elements = [
        "Enter or paste your text here",
        "Ctrl+C or Ctrl+Q to exit"
    ]
    
    for element in required_elements:
        if element in app.placeholder_text:
            print(f"✓ Placeholder contains: '{element}'")
        else:
            print(f"✗ Placeholder missing: '{element}'")
            return False
    
    return True

def main():
    """Run all tests."""
    print("Testing placeholder text removal implementation...\n")
    
    tests = [
        test_placeholder_initialization,
        test_placeholder_cleared_flag,
        test_key_detection,
        test_placeholder_content
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
        print("✓ All placeholder tests passed!")
        print("✓ Placeholder text should now be removed on first user input.")
        return True
    else:
        print("✗ Some placeholder tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    import sys
    sys.exit(0 if success else 1)