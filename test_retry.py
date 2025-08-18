#!/usr/bin/env python3
"""
Test the retry functionality for individual narrative objects.
"""
import asyncio
from llm_client import LLMClient
from object_manager import ObjectManager
from tui_app import LiterateApp

def test_retry_llm_prompt():
    """Test the LLM correction prompt."""
    print("🧪 Testing Retry LLM Integration")
    print("=" * 40)
    
    client = LLMClient()
    
    # Test correction prompt creation
    test_cases = [
        {
            "object_name": "detective", 
            "text": "Alice and Bob visited the old library.",
            "expected": "Should correct 'detective' to a proper name or remove it"
        },
        {
            "object_name": "BadName",
            "text": "Emma found a golden key in the castle.",
            "expected": "Should suggest a better name based on the actual text"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: '{case['object_name']}' in '{case['text']}'")
        print(f"   Expected: {case['expected']}")
        
        try:
            corrected = client.correct_narrative_object(case['object_name'], case['text'])
            if corrected:
                print(f"   ✅ Corrected to: '{corrected.name}' - {corrected.description}")
            else:
                print(f"   ❌ No correction generated")
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_object_replacement():
    """Test object replacement in manager."""
    print("\n🔧 Testing Object Replacement")
    print("=" * 35)
    
    manager = ObjectManager()
    
    # Add some test objects first
    from models import NarrativeObject
    from datetime import datetime
    
    original_obj = NarrativeObject(
        name="TestObject",
        description="Original description"
    )
    
    corrected_obj = NarrativeObject(
        name="CorrectedObject", 
        description="Better description"
    )
    
    # Add original object
    manager.collection.add_or_update(original_obj)
    print(f"Added: {original_obj.name}")
    
    # Test replacement
    result = manager.replace_object("TestObject", corrected_obj)
    
    if result["success"]:
        print(f"✅ Successfully replaced '{original_obj.name}' with '{corrected_obj.name}'")
        print(f"Stats: {result['stats']}")
    else:
        print(f"❌ Replacement failed: {result['error']}")
    
    # Test replacing non-existent object
    result2 = manager.replace_object("NonExistent", corrected_obj)
    if not result2["success"]:
        print(f"✅ Correctly rejected non-existent object: {result2['error']}")
    else:
        print(f"❌ Should have failed for non-existent object")

class RetryTestApp(LiterateApp):
    """Test app for retry functionality."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.test_completed = False
    
    async def on_mount(self) -> None:
        """Start test on mount."""
        super().on_mount()
        await self.run_retry_test()
    
    async def run_retry_test(self) -> None:
        """Run automated retry test."""
        await asyncio.sleep(1)
        
        # Set some test text
        self.current_input_text = "The detective investigated the mysterious library."
        
        # Simulate having objects
        from models import NarrativeObject
        test_obj = NarrativeObject(
            name="detective",
            description="Generic unnamed character"
        )
        self.object_manager.collection.add_or_update(test_obj)
        self.update_objects_display([test_obj])
        
        self.show_message("🧪 Test Setup Complete", "success")
        self.show_message("Try pressing 'r1' to retry the detective object", "info") 
        self.show_message("Or type new text to test full retry workflow", "info")

def main():
    """Run all retry tests."""
    print("Retry Functionality Testing")
    print("=" * 30)
    
    # Test components individually
    test_retry_llm_prompt()
    test_object_replacement()
    
    print("\n🚀 Starting Interactive Retry Test")
    print("This will launch the TUI with retry functionality enabled.")
    print("Instructions:")
    print("1. Enter some text with objects")
    print("2. Press r1, r2, etc. to retry specific objects")
    print("3. Watch for correction messages")
    print()
    
    # Run interactive test
    app = RetryTestApp()
    app.run()

if __name__ == "__main__":
    main()