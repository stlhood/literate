#!/usr/bin/env python3
"""
Test word wrapping in the narrative objects display.
"""
from tui_app import LiterateApp
from models import NarrativeObject

class WordWrapTestApp(LiterateApp):
    """Test app for word wrapping functionality."""
    
    def on_mount(self) -> None:
        """Setup test with long descriptions."""
        super().on_mount()
        
        # Create objects with various description lengths
        test_objects = [
            NarrativeObject(
                name="Alice",
                description="A young woman with long brown hair who works as a detective in the small town of Millbrook and has a passion for solving mysterious cases."
            ),
            NarrativeObject(
                name="Library",
                description="An enormous Victorian-era library with tall wooden shelves, ornate reading desks, and thousands of ancient books containing secrets."
            ),
            NarrativeObject(
                name="Bob",
                description="Short description."
            ),
            NarrativeObject(
                name="MysteriousBook", 
                description="This incredibly ancient and leather-bound tome contains mystical knowledge about dragons, magic spells, and forgotten civilizations that once ruled the world centuries ago."
            )
        ]
        
        # Add objects to manager
        for obj in test_objects:
            self.object_manager.collection.add_or_update(obj)
        
        # Set test input text
        self.current_input_text = "Alice found Bob reading a mysterious book in the old library."
        
        # Update display
        self.update_objects_display(test_objects)
        
        self.show_message("🧪 Word Wrap Test Active", "success") 
        self.show_message("Check how long descriptions are wrapped in the objects panel", "info")
        self.show_message("Try Ctrl+1, Ctrl+4 to test retry with long descriptions", "info")

def main():
    """Run word wrap test."""
    print("📝 Word Wrap Test for Narrative Objects Display")
    print("=" * 50)
    print("This test shows how long object descriptions are wrapped.")
    print("Look at the top-right panel to see:")
    print("• Long descriptions wrapped to multiple lines") 
    print("• Proper indentation for continuation lines")
    print("• Maintained tree structure with relationships")
    print()
    
    app = WordWrapTestApp()
    app.run()

if __name__ == "__main__":
    main()