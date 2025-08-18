"""
Textual TUI application for Literate.
"""
from textual.app import App, ComposeResult
from textual.widgets import TextArea, Static, RichLog
from textual.containers import Horizontal, Vertical, ScrollableContainer
from textual.screen import Screen
from textual.message import Message
from rich.text import Text
from rich.panel import Panel
from rich.console import Group
from typing import List
import asyncio
from datetime import datetime
from models import NarrativeObject
from object_manager import ObjectManager
from llm_client import LLMClient


class LiterateApp(App):
    """Main TUI application for Literate."""
    
    # Class variables for debouncing
    DEBOUNCE_SECONDS = 3.0
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.object_manager = ObjectManager()
        self.llm_client = LLMClient()
        self.debounce_task = None
        self.last_text = ""
        self.is_processing = False
    
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
        try:
            self.show_message("Ready to analyze text...", "info")
            self.update_objects_display([])
        except Exception as e:
            # Fallback if UI not ready yet
            pass
    
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
        try:
            error_log = self.query_one("#error_display", RichLog)
        except:
            # UI not ready yet, skip message
            return
        
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
    
    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        """Handle text area change events with debouncing."""
        if event.text_area.id != "text_input":
            return
        
        current_text = event.text_area.text
        
        # Skip if text hasn't actually changed
        if current_text == self.last_text:
            return
        
        self.last_text = current_text
        
        # Cancel existing debounce task
        if self.debounce_task:
            self.debounce_task.cancel()
        
        # Don't process empty text
        if not current_text.strip():
            self.update_objects_display([])
            self.show_message("Enter text to begin analysis...", "info")
            return
        
        # Show that we're waiting for more input
        self.show_message(f"Text changed... waiting {self.DEBOUNCE_SECONDS}s for more input", "info")
        
        # Schedule new debounce task
        self.debounce_task = asyncio.create_task(self._debounced_process_text(current_text))
    
    async def _debounced_process_text(self, text: str) -> None:
        """Process text after debounce delay."""
        try:
            # Wait for the debounce period with countdown
            for i in range(int(self.DEBOUNCE_SECONDS), 0, -1):
                self.show_message(f"⏳ Analysis starts in {i}s... (type to reset)", "info")
                await asyncio.sleep(1)
            
            # Check if we're already processing
            if self.is_processing:
                self.show_message("⚠️ Already processing previous request - please wait...", "warning")
                return
            
            # Start processing
            self.is_processing = True
            self.show_message("🤖 Analyzing text with LLM... ⚡", "info")
            self._show_loading_indicator()
            
            # Call LLM in a separate thread to avoid blocking
            await self._process_with_llm(text)
            
        except asyncio.CancelledError:
            # Task was cancelled due to new input
            self.show_message("⚡ Analysis cancelled - new input detected", "info")
            self._hide_loading_indicator()
        except Exception as e:
            self.show_message(f"❌ Error in debounce processing: {e}", "error")
            self._hide_loading_indicator()
        finally:
            self.is_processing = False
            self._hide_loading_indicator()
    
    async def _process_with_llm(self, text: str) -> None:
        """Process text with LLM in a non-blocking way."""
        try:
            # Run LLM processing in thread pool to avoid blocking
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                loop = asyncio.get_event_loop()
                
                # Get LLM response
                response = await loop.run_in_executor(
                    executor, 
                    self._get_llm_response, 
                    text
                )
                
                # Process the response
                result = await loop.run_in_executor(
                    executor, 
                    self.object_manager.process_text_update, 
                    text, 
                    response
                )
                
                # Update UI on main thread
                self._update_ui_from_result(result)
                
        except Exception as e:
            self.show_message(f"Error processing with LLM: {e}", "error")
    
    def _get_llm_response(self, text: str) -> str:
        """Get response from LLM - runs in thread pool."""
        try:
            prompt = self.llm_client._create_extraction_prompt(text)
            response = self.llm_client._call_ollama(prompt)
            return response.get("response", "")
        except Exception as e:
            raise Exception(f"LLM call failed: {e}")
    
    def _update_ui_from_result(self, result: dict) -> None:
        """Update UI based on processing result."""
        if result["success"]:
            objects = result["objects"]
            stats = result["stats"]
            
            # Update object display
            self.update_objects_display(objects)
            
            # Show success message with stats
            added = stats["added"]
            updated = stats["updated"] 
            removed = stats["removed"]
            total = result["total_count"]
            
            message = f"✅ Analysis complete: {total} objects ({added} added, {updated} updated, {removed} removed)"
            self.show_message(message, "success")
        else:
            # Show error
            error_msg = result.get("error", "Unknown error")
            self.show_message(f"❌ Analysis failed: {error_msg}", "error")
            
            # Still update display with current objects
            self.update_objects_display(result["objects"])
    
    def _show_loading_indicator(self) -> None:
        """Show loading indicator in objects display."""
        try:
            objects_log = self.query_one("#objects_display", RichLog)
            objects_log.write("[bold yellow]🔄 Processing with LLM...[/bold yellow]")
            objects_log.write("[dim]Please wait while we extract narrative objects...[/dim]")
        except:
            # UI not ready, skip
            pass
    
    def _hide_loading_indicator(self) -> None:
        """Hide loading indicator - will be replaced by results."""
        # Loading indicator will be cleared when results are displayed
        # No explicit action needed as update_objects_display clears the log
        pass


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