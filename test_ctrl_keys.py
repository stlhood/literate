#!/usr/bin/env python3
"""
Test Control key combinations for retry functionality.
"""
import asyncio
from tui_app import LiterateApp
from models import NarrativeObject

class ControlKeyTestApp(LiterateApp):
    """Test app for Control key functionality."""
    
    def on_mount(self) -> None:
        """Setup test environment."""
        super().on_mount()
        
        # Add some test objects
        test_objects = [
            NarrativeObject(name="TestObject1", description="First test object"),
            NarrativeObject(name="TestObject2", description="Second test object"),
            NarrativeObject(name="TestObject3", description="Third test object")
        ]
        
        for obj in test_objects:
            self.object_manager.collection.add_or_update(obj)
        
        # Set current input text for retry context
        self.current_input_text = "Alice and Bob visited the mysterious library."
        
        # Update display
        self.update_objects_display(test_objects)
        
        # Show instructions
        self.show_message("🧪 Control Key Test Ready", "success")
        self.show_message("Try pressing Ctrl+1, Ctrl+2, or Ctrl+3 to test retry", "info")
        self.show_message("Watch the messages panel for feedback", "info")
    
    def on_key(self, event) -> None:
        """Enhanced key handler with debugging."""
        # Debug: Show what key was pressed
        self.show_message(f"🔍 Key pressed: '{event.key}'", "info")
        
        # Call parent handler
        super().on_key(event)

def main():
    """Run Control key test."""
    print("🎮 Control Key Test for Retry Functionality")
    print("=" * 50)
    print("This will launch a test TUI with some sample objects.")
    print("Try pressing:")
    print("  • Ctrl+1 to retry first object")
    print("  • Ctrl+2 to retry second object") 
    print("  • Ctrl+3 to retry third object")
    print("Watch the message panel for key detection feedback.")
    print()
    
    app = ControlKeyTestApp()
    app.run()

if __name__ == "__main__":
    main()