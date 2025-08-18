#!/usr/bin/env python3
"""
Test script for debounce functionality.
"""
import asyncio
import time
from tui_app import LiterateApp


async def test_debounce_simulation():
    """Simulate debounce behavior without actually running the TUI."""
    app = LiterateApp()
    
    # Initialize the app components
    app.object_manager = app.object_manager
    app.llm_client = app.llm_client
    
    print("=== Testing Debounce Logic ===")
    
    # Test 1: Rapid text changes should cancel previous debounce
    print("\n1. Testing rapid text changes...")
    
    # Mock text area for testing
    class MockTextArea:
        def __init__(self, text=""):
            self.text = text
            self.id = "text_input"
    
    class MockEvent:
        def __init__(self, text):
            self.text_area = MockTextArea(text)
    
    # Simulate rapid typing
    texts = ["H", "He", "Hel", "Hell", "Hello", "Hello world", "Hello world!"]
    
    for i, text in enumerate(texts):
        print(f"  Input {i+1}: '{text}'")
        app.last_text = ""  # Force change detection
        
        # Simulate the text change event
        event = MockEvent(text)
        app.on_text_area_changed(event)
        
        # Wait a short time to simulate typing speed
        await asyncio.sleep(0.5)
    
    print(f"  Final text: '{app.last_text}'")
    print(f"  Debounce task active: {app.debounce_task is not None and not app.debounce_task.done()}")
    
    # Test 2: Wait for debounce to complete
    print("\n2. Testing debounce completion...")
    if app.debounce_task and not app.debounce_task.done():
        print("  Waiting for debounce to complete...")
        start_time = time.time()
        
        try:
            await app.debounce_task
            elapsed = time.time() - start_time
            print(f"  ✓ Debounce completed after {elapsed:.2f} seconds")
        except Exception as e:
            print(f"  ✗ Debounce failed: {e}")
    
    # Test 3: Empty text handling
    print("\n3. Testing empty text handling...")
    empty_event = MockEvent("")
    app.on_text_area_changed(empty_event)
    print(f"  Empty text processed, no debounce task: {app.debounce_task is None or app.debounce_task.done()}")
    
    # Test 4: Same text handling
    print("\n4. Testing duplicate text handling...")
    app.last_text = "Same text"
    same_event = MockEvent("Same text")
    original_task = app.debounce_task
    app.on_text_area_changed(same_event)
    print(f"  Same text ignored, task unchanged: {app.debounce_task == original_task}")
    
    print("\n=== Debounce Tests Complete ===")


def test_interactive_debounce():
    """Run interactive debounce test with real TUI."""
    print("=== Interactive Debounce Test ===")
    print("Instructions:")
    print("1. Type some text and wait 3 seconds")
    print("2. Try typing and then typing more before 3 seconds")
    print("3. Try pasting text")
    print("4. Watch the message panel for debounce status")
    print("5. Press Ctrl+C to exit")
    print()
    
    app = LiterateApp()
    
    # Override some methods for testing
    original_process_with_llm = app._process_with_llm
    
    async def mock_process_with_llm(text: str):
        """Mock LLM processing for testing."""
        try:
            app.show_message("🧪 MOCK: Processing text with fake LLM...", "info")
            await asyncio.sleep(2)  # Simulate processing time
            
            # Create mock result
            result = {
                "success": True,
                "objects": [],  # Empty for test
                "total_count": 0,
                "stats": {"added": 0, "updated": 0, "removed": 0, "unchanged": 0}
            }
            
            app._update_ui_from_result(result)
            app.show_message(f"🧪 MOCK: Processed {len(text)} characters", "success")
            
        except Exception as e:
            app.show_message(f"🧪 MOCK: Error: {e}", "error")
    
    app._process_with_llm = mock_process_with_llm
    
    # Add instructions to the initial display
    def enhanced_on_mount():
        app.query_one("#text_input", app.TextArea).focus()
        app.show_message("🧪 DEBOUNCE TEST MODE - LLM calls are mocked", "info")
        app.show_message("Type to see debounce behavior...", "info")
        app.update_objects_display([])
    
    app.on_mount = enhanced_on_mount
    
    # Run the app
    try:
        app.run()
    except KeyboardInterrupt:
        print("\n\nDebounce test completed!")


async def test_performance():
    """Test performance of debounce mechanism."""
    print("=== Performance Test ===")
    
    app = LiterateApp()
    
    # Test many rapid changes
    start_time = time.time()
    
    class MockTextArea:
        def __init__(self, text=""):
            self.text = text
            self.id = "text_input"
    
    class MockEvent:
        def __init__(self, text):
            self.text_area = MockTextArea(text)
    
    # Simulate very rapid typing
    for i in range(100):
        text = f"Performance test text number {i}"
        event = MockEvent(text)
        app.last_text = ""  # Force change detection
        app.on_text_area_changed(event)
        await asyncio.sleep(0.01)  # Very fast typing
    
    elapsed = time.time() - start_time
    print(f"Processed 100 rapid changes in {elapsed:.3f} seconds")
    
    # Check final state
    active_task = app.debounce_task is not None and not app.debounce_task.done()
    print(f"Final debounce task active: {active_task}")
    
    if active_task:
        print("Waiting for final debounce...")
        try:
            await app.debounce_task
            print("✓ Final debounce completed successfully")
        except Exception as e:
            print(f"✗ Final debounce failed: {e}")


def main():
    """Run all debounce tests."""
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "interactive":
            test_interactive_debounce()
        elif sys.argv[1] == "performance":
            asyncio.run(test_performance())
        else:
            print("Usage: python test_debounce.py [interactive|performance]")
    else:
        asyncio.run(test_debounce_simulation())


if __name__ == "__main__":
    main()