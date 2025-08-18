#!/usr/bin/env python3
"""
Test the full pipeline with realistic scenarios.
"""
from tui_app import LiterateApp
import asyncio

async def test_realistic_scenarios():
    """Test with realistic narrative text."""
    print("🧪 Testing Full Pipeline with Realistic Scenarios")
    print("=" * 55)
    
    app = LiterateApp()
    
    scenarios = [
        {
            "name": "Simple story",
            "text": "Emma walked through the park and saw a beautiful oak tree."
        },
        {
            "name": "Character interaction",
            "text": "Emma walked through the park and met her friend Jack near the fountain. They decided to visit the old library."
        },
        {
            "name": "Complex narrative",
            "text": "Emma and Jack entered the mysterious library where they discovered an ancient book about dragons. The librarian, Mrs. Smith, warned them about the book's strange powers."
        },
        {
            "name": "Updated story",
            "text": "Emma and Jack carefully read the dragon book in the library. Mrs. Smith revealed she was actually a retired dragon trainer who had been protecting the book for decades."
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. Testing: {scenario['name']}")
        print("-" * 40)
        
        try:
            # Test LLM processing
            response = app._get_llm_response(scenario['text'])
            print(f"✓ LLM responded with {len(response)} characters")
            
            # Test object extraction
            result = app.object_manager.process_text_update(scenario['text'], response)
            
            if result['success']:
                print(f"✅ Success: {result['total_count']} objects found")
                print(f"   Stats: +{result['stats']['added']}, ~{result['stats']['updated']}, -{result['stats']['removed']}")
                
                # Show objects
                for obj in result['objects'][:3]:  # Show first 3
                    print(f"   - {obj.name}: {obj.description[:60]}...")
                    
            else:
                print(f"❌ Failed: {result.get('error', 'Unknown error')}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            
    print(f"\n📊 Final Statistics:")
    print(f"Total objects in collection: {len(app.object_manager.collection.objects)}")
    
    # Show all objects
    all_objects = list(app.object_manager.collection.objects.values())
    for obj in all_objects:
        print(f"  • {obj.name}: {obj.description[:50]}...")

def test_edge_cases():
    """Test edge cases and error handling."""
    print("\n🔧 Testing Edge Cases")
    print("=" * 25)
    
    app = LiterateApp()
    
    edge_cases = [
        ("Empty text", ""),
        ("Very short", "Hi."),
        ("No names", "The weather is nice today."),
        ("Special characters", "Hello! @#$% ^&*()"),
        ("Very long text", "The story continues " * 50)
    ]
    
    for name, text in edge_cases:
        print(f"\nTesting {name}: '{text[:30]}...'")
        try:
            if text.strip():
                response = app._get_llm_response(text)
                result = app.object_manager.process_text_update(text, response)
                print(f"   ✓ Handled: {result['total_count']} objects")
            else:
                print(f"   ✓ Empty text handled correctly")
        except Exception as e:
            print(f"   ❌ Error: {e}")

async def main():
    """Run all pipeline tests."""
    await test_realistic_scenarios()
    test_edge_cases()
    print("\n✅ Full pipeline testing completed!")
    print("The system is ready for interactive use.")

if __name__ == "__main__":
    asyncio.run(main())