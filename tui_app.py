"""
Textual TUI application for Literate.
"""
from textual.app import App, ComposeResult
from textual.widgets import TextArea, Static, RichLog
from textual.containers import Horizontal, Vertical, ScrollableContainer
from textual.screen import Screen
from textual.message import Message
from textual.events import Click, Key
from rich.text import Text
from rich.panel import Panel
from rich.console import Group
from typing import List
import asyncio
import signal
import sys
from datetime import datetime
from models import NarrativeObject
from object_manager import ObjectManager
from llm_client import LLMClient


class LiterateApp(App):
    """Main TUI application for Literate."""
    
    # Class variables for debouncing
    DEBOUNCE_SECONDS = 3.0
    
    # Disable mouse tracking to prevent unwanted mouse interactions
    ENABLE_COMMAND_PALETTE = False
    
    @property
    def mouse_enabled(self) -> bool:
        """Disable mouse tracking."""
        return False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.object_manager = ObjectManager()
        self.llm_client = LLMClient()
        self.debounce_task = None
        self.last_text = ""
        self.is_processing = False
        self.current_input_text = ""  # Store for retry functionality
        self.displayed_objects = []  # Store currently displayed objects for retry
        self.placeholder_text = "Enter or paste your text here...\nPress Ctrl+C or Ctrl+Q to exit."
        self.placeholder_cleared = False  # Track if placeholder has been cleared
        self._setup_signal_handlers()
    
    CSS = """
    Screen {
        layout: horizontal;
        background: $surface;
    }
    
    #text_input_container {
        width: 50%;
        height: 100%;
        border: thick $primary 60%;
        background: $panel;
        border-title-color: $primary;
        border-title-background: $surface;
        border-title-style: bold;
    }
    
    #right_container {
        width: 50%;
        height: 100%;
        layout: vertical;
    }
    
    #objects_container {
        height: 80%;
        border: thick $success 80%;
        background: $panel;
        border-title-color: $success;
        border-title-background: $surface;
        border-title-style: bold;
    }
    
    #error_container {
        height: 20%;
        border: thick $accent 60%;
        background: $panel;
        border-title-color: $accent;
        border-title-background: $surface;
        border-title-style: bold;
    }
    
    #text_input {
        height: 100%;
        width: 100%;
        background: $surface;
        color: $text;
    }
    
    #objects_display {
        height: 100%;
        width: 100%;
        padding: 1;
        background: $surface;
        scrollbar-background: $panel;
        scrollbar-color: $primary;
    }
    
    #error_display {
        height: 100%;
        width: 100%;
        padding: 1;
        background: $surface;
        scrollbar-background: $panel;
        scrollbar-color: $accent;
    }
    
    .object_item {
        margin: 1 0;
        padding: 1;
        background: $boost;
        border: round $primary 30%;
    }
    
    .object_name {
        text-style: bold;
        color: $primary;
    }
    
    .object_description {
        color: $text-muted;
        margin: 0 0 1 0;
        text-style: italic;
    }
    
    .relationship {
        color: $success;
        text-style: italic;
        margin-left: 2;
    }
    
    .panel_title {
        text-style: bold;
        color: white;
        text-align: center;
        height: 1;
        background: $primary;
        padding: 0 1;
    }
    
    .status_processing {
        color: $warning;
        text-style: bold blink;
    }
    
    .status_success {
        color: $success;
        text-style: bold;
    }
    
    .status_error {
        color: $error;
        text-style: bold;
    }
    
    .stats_display {
        color: $accent;
        text-style: italic;
        background: $boost;
        padding: 0 1;
        margin: 1 0;
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
                    text=self.placeholder_text,
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
        # Comprehensive mouse tracking disable at startup
        self._cleanup_terminal_state()
        
        # Focus the text input area
        self.query_one("#text_input", TextArea).focus()
        
        # Initialize displays
        try:
            self.show_message("Ready to analyze text...", "info")
            self.show_message("💡 Tip: Use Ctrl+1, Ctrl+2, etc. to retry individual objects", "info")
            self.show_message("🚪 Exit with Ctrl+C or Ctrl+Q", "info")
            self.update_objects_display([])
        except Exception as e:
            # Fallback if UI not ready yet
            pass
    
    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful exit."""
        def signal_handler(signum, frame):
            """Handle SIGINT (Ctrl+C) gracefully."""
            self._graceful_exit()
        
        # Register signal handler for SIGINT (Ctrl+C)
        signal.signal(signal.SIGINT, signal_handler)
    
    def _graceful_exit(self) -> None:
        """Perform graceful shutdown with comprehensive cleanup."""
        try:
            # Cancel any pending debounce task
            if self.debounce_task and not self.debounce_task.done():
                self.debounce_task.cancel()
            
            # Show exit message
            self.show_message("🔄 Shutting down gracefully...", "info")
            
            # Save any pending data (if needed)
            if hasattr(self.object_manager, 'save_file') and self.object_manager.save_file:
                self.object_manager.save_to_file(self.object_manager.save_file)
                self.show_message("💾 Data saved", "success")
            
        except Exception as e:
            print(f"Error during shutdown: {e}", file=sys.stderr)
        finally:
            # Comprehensive mouse tracking cleanup to prevent control character leakage
            self._cleanup_terminal_state()
            # Exit the application
            self.exit()
    
    def _cleanup_terminal_state(self) -> None:
        """Clean up terminal state to prevent mouse control character leakage."""
        try:
            import os
            import sys
            
            # Comprehensive mouse tracking disable sequence
            # This covers all major mouse tracking modes that could leak control chars
            cleanup_sequence = (
                "\033[?1000l"  # Disable X10 mouse reporting
                "\033[?1001l"  # Disable highlight mouse tracking
                "\033[?1002l"  # Disable cell motion mouse tracking  
                "\033[?1003l"  # Disable all motion mouse tracking
                "\033[?1004l"  # Disable focus in/out events
                "\033[?1005l"  # Disable UTF-8 mouse mode
                "\033[?1006l"  # Disable SGR extended mouse mode
                "\033[?1015l"  # Disable urxvt extended mouse mode
                "\033[?25h"    # Show cursor (re-enable if hidden)
                "\033[0m"      # Reset all text attributes
            )
            
            # Write directly to stderr to bypass any TUI handling
            sys.stderr.write(cleanup_sequence)
            sys.stderr.flush()
            
            # Also use os.system as backup (the original approach)
            os.system('printf "\\033[?1000l\\033[?1002l\\033[?1003l\\033[?1006l\\033[?25h"')
            
        except Exception as e:
            # If cleanup fails, at least try basic reset
            try:
                import sys
                sys.stderr.write("\033[0m\033[?25h")
                sys.stderr.flush()
            except:
                pass
    
    def action_quit(self) -> None:
        """Action to quit the application."""
        self._graceful_exit()
    
    async def action_retry_object(self, object_name: str) -> None:
        """Action to retry a specific narrative object."""
        await self._retry_narrative_object(object_name)
    
    async def _retry_narrative_object(self, object_name: str) -> None:
        """Retry extraction for a specific narrative object."""
        if not self.current_input_text.strip():
            self.show_message("No input text available for retry", "warning")
            return
        
        if self.is_processing:
            self.show_message("Cannot retry while processing - please wait", "warning")
            return
        
        self.show_message(f"🔄 Correcting object '{object_name}'...", "info")
        self.is_processing = True
        
        try:
            # Call LLM for correction in thread pool
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                loop = asyncio.get_event_loop()
                
                corrected_object = await loop.run_in_executor(
                    executor,
                    self.llm_client.correct_narrative_object,
                    object_name,
                    self.current_input_text
                )
                
                if corrected_object:
                    # Replace the object
                    result = self.object_manager.replace_object(object_name, corrected_object)
                    
                    if result["success"]:
                        # Update display
                        self.update_objects_display(result["objects"])
                        self.show_message(f"✅ Object '{object_name}' corrected to '{corrected_object.name}'", "success")
                    else:
                        self.show_message(f"❌ Failed to replace object: {result['error']}", "error")
                else:
                    self.show_message(f"❌ Could not generate correction for '{object_name}'", "error")
        
        except Exception as e:
            self.show_message(f"❌ Error during retry: {e}", "error")
        finally:
            self.is_processing = False
    
    def on_key(self, event: Key) -> None:
        """Handle key presses for retry functionality and exit handling."""
        # Handle Control-Q for exit
        if event.key == 'ctrl+q':
            event.prevent_default()
            self._graceful_exit()
            return
        
        # Clear placeholder text on first keypress (if focused on text input)
        if not self.placeholder_cleared:
            focused = self.focused
            if focused and focused.id == "text_input":
                # Check if it's a regular typing key (not navigation keys)
                if (len(event.key) == 1 or 
                    event.key in ['space', 'enter', 'backspace', 'delete', 'tab']):
                    text_area = self.query_one("#text_input", TextArea)
                    if text_area.text == self.placeholder_text:
                        text_area.text = ""
                        self.placeholder_cleared = True
        
        # Check for Ctrl+number combinations for retry
        if event.key.startswith('ctrl+') and len(event.key) > 5:
            try:
                # Extract number from key (e.g., 'ctrl+1' -> 1)
                number_str = event.key[5:]  # Remove 'ctrl+' prefix
                object_index = int(number_str) - 1  # Convert to 0-based index
                
                # Check if we have that many displayed objects
                if 0 <= object_index < len(self.displayed_objects):
                    object_name = self.displayed_objects[object_index].name
                    # Create task for retry action
                    asyncio.create_task(self._retry_narrative_object(object_name))
                    event.prevent_default()
                    self.show_message(f"🔄 Retrying object {object_index + 1}: {object_name}", "info")
                else:
                    self.show_message(f"No object at position {object_index + 1}", "warning")
                    event.prevent_default()
            except ValueError:
                # Not a valid retry key combination
                pass
    
    def _wrap_description(self, text: str, max_width: int = 35) -> List[str]:
        """
        Wrap text description to fit within the display width.
        
        Args:
            text: Text to wrap
            max_width: Maximum characters per line
            
        Returns:
            List of wrapped lines
        """
        if len(text) <= max_width:
            return [text]
        
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            # Check if adding this word would exceed the line width
            word_length = len(word)
            space_length = 1 if current_line else 0
            
            if current_length + space_length + word_length <= max_width:
                # Word fits on current line
                current_line.append(word)
                current_length += space_length + word_length
            else:
                # Start new line
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
                current_length = word_length
        
        # Add remaining words
        if current_line:
            lines.append(" ".join(current_line))
        
        return lines if lines else [text]
    
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
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Enhanced styling based on message type
        if msg_type == "error":
            icon = "🔴"
            style_class = "status_error"
            formatted_message = f"[dim]{timestamp}[/dim] [{style_class}]{icon} {message}[/{style_class}]"
        elif msg_type == "warning":
            icon = "🟡"
            style_class = "status_processing"
            formatted_message = f"[dim]{timestamp}[/dim] [{style_class}]{icon} {message}[/{style_class}]"
        elif msg_type == "success":
            icon = "🟢"
            style_class = "status_success"
            formatted_message = f"[dim]{timestamp}[/dim] [{style_class}]{icon} {message}[/{style_class}]"
        else:  # info
            icon = "🔵"
            formatted_message = f"[dim]{timestamp}[/dim] [blue]{icon} {message}[/blue]"
        
        error_log.write(formatted_message)
    
    def update_objects_display(self, objects: List[NarrativeObject]) -> None:
        """
        Update the objects display panel with enhanced formatting and performance optimization.
        
        Args:
            objects: List of narrative objects to display
        """
        objects_log = self.query_one("#objects_display", RichLog)
        objects_log.clear()
        
        if not objects:
            objects_log.write("[dim italic]✨ No narrative objects found yet...[/dim italic]")
            objects_log.write("[dim]Type some text to begin analysis![/dim]")
            return
        
        # Sort objects by last updated (most recent first)
        sorted_objects = sorted(objects, key=lambda x: x.last_updated, reverse=True)
        
        # Performance optimization: Limit display to prevent UI slowdown
        max_display_objects = 20
        display_objects = sorted_objects[:max_display_objects]
        hidden_count = len(sorted_objects) - len(display_objects)
        
        # Store displayed objects for retry functionality
        self.displayed_objects = display_objects
        
        # Header with stats
        total_relationships = sum(len(obj.relationships) for obj in objects)
        objects_log.write(f"[bold $primary]📚 Narrative Objects ({len(objects)})[/bold $primary]")
        objects_log.write(f"[dim]🔗 {total_relationships} relationships found[/dim]")
        
        if hidden_count > 0:
            objects_log.write(f"[dim italic]Showing most recent {len(display_objects)} of {len(objects)} objects[/dim italic]")
        objects_log.write("")
        
        for i, obj in enumerate(display_objects, 1):
            # Object card with rounded border effect and retry link
            objects_log.write(f"[bold $success]┌─ {i}. {obj.name}[/bold $success] [dim]([link=retry]🔄 press Ctrl+{i} to retry[/link])[/dim]")
            
            # Description with word wrapping and proper indentation
            description = obj.description
            # Split long descriptions into multiple lines with proper indentation
            description_lines = self._wrap_description(description, max_width=35)
            for j, line in enumerate(description_lines):
                if j == 0:
                    objects_log.write(f"[dim]│[/dim] [italic $text-muted]{line}[/italic $text-muted]")
                else:
                    objects_log.write(f"[dim]│[/dim] [italic $text-muted]  {line}[/italic $text-muted]")
            
            # Relationships with tree structure (limit to prevent clutter)
            if obj.relationships:
                objects_log.write(f"[dim]│[/dim] [bold $accent]Relationships:[/bold $accent]")
                display_rels = obj.relationships[:3]  # Show max 3 relationships
                hidden_rels = len(obj.relationships) - len(display_rels)
                
                for j, rel in enumerate(display_rels):
                    is_last = j == len(display_rels) - 1 and hidden_rels == 0
                    connector = "└" if is_last else "├"
                    objects_log.write(f"[dim]│ {connector}─[/dim] [bold $primary]{rel.target}[/bold $primary]: [italic]{rel.description}[/italic]")
                
                if hidden_rels > 0:
                    objects_log.write(f"[dim]│ └─[/dim] [dim italic]... and {hidden_rels} more relationships[/dim italic]")
            
            # Timestamp
            time_str = obj.last_updated.strftime("%H:%M:%S")
            objects_log.write(f"[dim]└─ Updated: {time_str}[/dim]")
            
            # Add spacing between objects
            if i < len(display_objects):
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
        """Handle text area change events with debouncing and performance optimization."""
        if event.text_area.id != "text_input":
            return
        
        current_text = event.text_area.text
        
        # Clear placeholder text on first user input
        if not self.placeholder_cleared and current_text != self.placeholder_text:
            # User has started typing/pasting - check if they're modifying the placeholder
            if current_text.startswith(self.placeholder_text) or self.placeholder_text.startswith(current_text):
                # User is editing the placeholder text, clear it completely
                event.text_area.text = ""
                current_text = ""
                self.placeholder_cleared = True
            elif current_text.strip():  # User pasted something completely different
                self.placeholder_cleared = True
        
        # Skip if text hasn't actually changed
        if current_text == self.last_text:
            return
        
        self.last_text = current_text
        self.current_input_text = current_text  # Store for retry functionality
        
        # Cancel existing debounce task
        if self.debounce_task:
            self.debounce_task.cancel()
        
        # Don't process empty text
        if not current_text.strip():
            self.update_objects_display([])
            self.show_message("Enter text to begin analysis...", "info")
            return
        
        # Performance optimization: Check text length
        text_length = len(current_text)
        if text_length > 5000:
            self.show_message(f"⚠️ Large text ({text_length} chars) - processing may take longer", "warning")
        elif text_length > 2000:
            self.show_message(f"📝 Processing {text_length} characters...", "info")
        else:
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
        """Update UI based on processing result with enhanced feedback and animation."""
        if result["success"]:
            objects = result["objects"]
            stats = result["stats"]
            
            # Animation: Show transition message
            added = stats["added"]
            updated = stats["updated"] 
            removed = stats["removed"]
            total = result["total_count"]
            
            if added > 0 or updated > 0 or removed > 0:
                self.show_message("✨ Updating narrative objects...", "info")
                # Brief delay for visual effect
                import time
                time.sleep(0.1)
            
            # Update object display
            self.update_objects_display(objects)
            
            # Enhanced success message with detailed stats
            stats_parts = []
            if added > 0:
                stats_parts.append(f"+{added} new")
            if updated > 0:
                stats_parts.append(f"~{updated} updated") 
            if removed > 0:
                stats_parts.append(f"-{removed} removed")
            
            if stats_parts:
                stats_text = " | ".join(stats_parts)
                message = f"Analysis complete: {total} objects ({stats_text})"
            else:
                message = f"Analysis complete: {total} objects (no changes)"
                
            self.show_message(message, "success")
            
        else:
            # Show detailed error with suggestions
            error_msg = result.get("error", "Unknown error")
            
            # Provide helpful error context
            if "connection" in error_msg.lower():
                suggestion = "Check that Ollama server is running"
            elif "json" in error_msg.lower():
                suggestion = "LLM response format issue - try different text"
            else:
                suggestion = "Try simpler text or restart the application"
                
            self.show_message(f"Analysis failed: {error_msg}", "error")
            self.show_message(f"💡 Suggestion: {suggestion}", "warning")
            
            # Still update display with current objects
            self.update_objects_display(result["objects"])
    
    def _show_loading_indicator(self) -> None:
        """Show enhanced loading indicator in objects display."""
        try:
            objects_log = self.query_one("#objects_display", RichLog)
            objects_log.clear()
            
            # Animated loading display
            objects_log.write("[bold $warning]⚡ Processing with LLM...[/bold $warning]")
            objects_log.write("[dim]┌─ Analyzing narrative structure...[/dim]")
            objects_log.write("[dim]├─ Extracting characters and objects...[/dim]") 
            objects_log.write("[dim]├─ Identifying relationships...[/dim]")
            objects_log.write("[dim]└─ Generating results...[/dim]")
            objects_log.write("")
            objects_log.write("[italic dim]🤖 Please wait while the AI processes your text...[/italic dim]")
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