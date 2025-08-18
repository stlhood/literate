"""
Textual TUI application for Literate.
"""
from textual.app import App, ComposeResult
from textual.widgets import TextArea, Static, RichLog
from textual.containers import Horizontal, Vertical, ScrollableContainer
from textual.screen import Screen
from rich.text import Text
from rich.panel import Panel
from rich.console import Group
from typing import List
from models import NarrativeObject


class LiterateApp(App):
    """Main TUI application for Literate."""
    
    CSS = """
    Screen {
        layout: horizontal;
    }
    
    #text_input_container {
        width: 50%;
        height: 100%;
        border: solid $primary;
    }
    
    #right_container {
        width: 50%;
        height: 100%;
        layout: vertical;
    }
    
    #objects_container {
        height: 80%;
        border: solid $secondary;
    }
    
    #error_container {
        height: 20%;
        border: solid $warning;
    }
    
    #text_input {
        height: 100%;
        width: 100%;
    }
    
    #objects_display {
        height: 100%;
        width: 100%;
        padding: 1;
    }
    
    #error_display {
        height: 100%;
        width: 100%;
        padding: 1;
    }
    
    .object_item {
        margin: 1 0;
        padding: 1;
        background: $boost;
    }
    
    .object_name {
        text-style: bold;
        color: $primary;
    }
    
    .object_description {
        color: $text;
        margin: 0 0 1 0;
    }
    
    .relationship {
        color: $secondary;
        text-style: italic;
        margin-left: 2;
    }
    
    .panel_title {
        text-style: bold;
        color: $primary;
        text-align: center;
        height: 1;
        background: $surface;
    }
    """
    
    TITLE = "Literate - Narrative Text Analyzer"
    SUB_TITLE = "Enter text in the left panel to extract narrative objects"
    
    def compose(self) -> ComposeResult:
        """Create the three-panel layout."""
        with Horizontal():
            # Left panel: Text input
            with Vertical(id="text_input_container"):
                yield Static("📝 Text Input", classes="panel_title")
                yield TextArea(
                    text="Enter or paste your text here...\nPress Ctrl+C to exit.",
                    id="text_input"
                )
            
            # Right panel: Split into objects and error display
            with Vertical(id="right_container"):
                # Top: Objects display
                with ScrollableContainer(id="objects_container"):
                    yield Static("🔍 Narrative Objects", classes="panel_title")
                    yield RichLog(id="objects_display", auto_scroll=True, markup=True)
                
                # Bottom: Error messages
                with ScrollableContainer(id="error_container"):
                    yield Static("💬 Messages", classes="panel_title") 
                    yield RichLog(id="error_display", auto_scroll=True, markup=True)
    
    def on_mount(self) -> None:
        """Called when the app is mounted."""
        # Focus the text input area
        self.query_one("#text_input", TextArea).focus()
        
        # Initialize displays
        self.show_message("Ready to analyze text...", "info")
        self.update_objects_display([])
    
    def action_quit(self) -> None:
        """Action to quit the application."""
        self.exit()
    
    def show_message(self, message: str, msg_type: str = "info") -> None:
        """
        Display a message in the error panel.
        
        Args:
            message: Message to display
            msg_type: Type of message (info, warning, error, success)
        """
        error_log = self.query_one("#error_display", RichLog)
        
        # Color based on message type
        if msg_type == "error":
            color = "red"
            icon = "❌"
        elif msg_type == "warning":
            color = "yellow"
            icon = "⚠️"
        elif msg_type == "success":
            color = "green"
            icon = "✅"
        else:  # info
            color = "blue"
            icon = "ℹ️"
        
        formatted_message = f"[{color}]{icon} {message}[/{color}]"
        error_log.write(formatted_message)
    
    def update_objects_display(self, objects: List[NarrativeObject]) -> None:
        """
        Update the objects display panel.
        
        Args:
            objects: List of narrative objects to display
        """
        objects_log = self.query_one("#objects_display", RichLog)
        objects_log.clear()
        
        if not objects:
            objects_log.write("[dim]No objects extracted yet.[/dim]")
            return
        
        # Sort objects by last updated (most recent first)
        sorted_objects = sorted(objects, key=lambda x: x.last_updated, reverse=True)
        
        objects_log.write(f"[bold cyan]Found {len(objects)} narrative objects:[/bold cyan]\n")
        
        for i, obj in enumerate(sorted_objects, 1):
            # Object header
            objects_log.write(f"[bold blue]{i}. {obj.name}[/bold blue]")
            
            # Description
            objects_log.write(f"   [dim]{obj.description}[/dim]")
            
            # Relationships
            if obj.relationships:
                objects_log.write(f"   [bold]Relationships:[/bold]")
                for rel in obj.relationships:
                    objects_log.write(f"   [green]→[/green] [italic]{rel.target}[/italic]: {rel.description}")
            
            # Add spacing between objects
            if i < len(sorted_objects):
                objects_log.write("")
    
    def get_input_text(self) -> str:
        """Get current text from the input area."""
        text_area = self.query_one("#text_input", TextArea)
        return text_area.text
    
    def clear_input_text(self) -> None:
        """Clear the input text area."""
        text_area = self.query_one("#text_input", TextArea)
        text_area.text = ""
    
    def set_input_text(self, text: str) -> None:
        """Set text in the input area."""
        text_area = self.query_one("#text_input", TextArea)
        text_area.text = text


class LiterateScreen(Screen):
    """Main screen for the Literate application."""
    
    def compose(self) -> ComposeResult:
        """Compose the screen layout."""
        yield from LiterateApp().compose()


def main():
    """Main entry point for the TUI application."""
    app = LiterateApp()
    app.run()


if __name__ == "__main__":
    main()