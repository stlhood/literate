#!/usr/bin/env python3
"""
Test real-time TUI updates with actual LLM processing
"""
from tui_app import LiterateApp
import asyncio
from textual.events import Key

class TestRealTimeApp(LiterateApp):
    """Extended app for testing real-time updates."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.test_texts = [
            "John walked through the forest.",
            "John walked through the forest and met Sarah by the river.",
            "John walked through the forest and met Sarah by the river. They found an old treasure map.",
            ""
        ]
        self.test_index = 0
    
    async def on_mount(self) -> None:
        """Auto-start testing when mounted."""
        await super().on_mount()
        # Start automated testing after a short delay
        await asyncio.sleep(1)
        await self.run_automated_test()
    
    async def run_automated_test(self) -> None:
        """Run automated real-time testing."""
        self.show_message("🧪 Starting automated real-time test...", "info")
        
        for i, test_text in enumerate(self.test_texts):
            self.show_message(f"Test {i+1}/4: Updating text...", "info")
            
            # Update text area
            text_area = self.query_one("#text_input")
            text_area.text = test_text
            
            # Trigger change event manually
            if test_text:  # Don't process empty text
                self.on_text_area_changed(
                    type('MockEvent', (), {
                        'text_area': type('MockTextArea', (), {
                            'id': 'text_input',
                            'text': test_text
                        })()
                    })()
                )
            
                # Wait for processing to complete
                await asyncio.sleep(self.DEBOUNCE_SECONDS + 2)
            else:
                self.show_message("Testing empty text handling...", "info")
                await asyncio.sleep(1)
        
        self.show_message("✅ Automated test completed! Try typing manually now.", "success")
    
    def action_next_test(self) -> None:
        """Action to trigger next test (bound to 'n' key)."""
        if self.test_index < len(self.test_texts):
            test_text = self.test_texts[self.test_index]
            self.show_message(f"Manual test {self.test_index + 1}: '{test_text[:30]}...'", "info")
            
            text_area = self.query_one("#text_input")
            text_area.text = test_text
            
            self.test_index += 1
        else:
            self.show_message("All manual tests completed!", "success")

def main():
    """Run the real-time testing app."""
    print("🚀 Starting Real-time TUI Test")
    print("After the automated test, you can:")
    print("  - Type text manually to test real-time processing")
    print("  - Press 'n' for next manual test")
    print("  - Press 'q' or Ctrl+C to quit")
    print()
    
    app = TestRealTimeApp()
    app.run()

if __name__ == "__main__":
    main()