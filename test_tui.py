#!/usr/bin/env python3
"""
Test script for the TUI functionality.
"""
from tui_app import LiterateApp
from models import NarrativeObject, Relationship
from datetime import datetime


def test_tui_formatting():
    """Test TUI with sample narrative objects."""
    # Create some sample narrative objects
    rel1 = Relationship("Bob", "Alice's close friend and research partner")
    rel2 = Relationship("Research Lab", "Works at the same laboratory")
    
    alice = NarrativeObject(
        name="Alice",
        description="A brilliant scientist working on artificial intelligence research.",
        relationships=[rel1, rel2],
        first_seen=datetime.now(),
        last_updated=datetime.now()
    )
    
    rel3 = Relationship("Alice", "Bob's research partner and friend")
    bob = NarrativeObject(
        name="Bob", 
        description="A dedicated researcher specializing in machine learning algorithms.",
        relationships=[rel3],
        first_seen=datetime.now(),
        last_updated=datetime.now()
    )
    
    lab = NarrativeObject(
        name="Research Lab",
        description="A cutting-edge facility for AI and ML research.",
        relationships=[],
        first_seen=datetime.now(),
        last_updated=datetime.now()
    )
    
    # Create the app
    app = LiterateApp()
    
    # Override the on_mount method to show test data
    original_on_mount = app.on_mount
    def test_on_mount():
        original_on_mount()
        app.show_message("Testing TUI with sample data", "info")
        app.show_message("Objects loaded successfully", "success")
        app.show_message("This is a warning message", "warning") 
        app.show_message("This would be an error", "error")
        app.update_objects_display([alice, bob, lab])
        app.set_input_text("This is sample text that would be analyzed by the LLM.\nYou can see how the three-panel layout works!")
    
    app.on_mount = test_on_mount
    
    # Run the app
    app.run()


if __name__ == "__main__":
    test_tui_formatting()