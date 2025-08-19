# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Literate is a Python-based command-line tool that uses a locally-running LLM to extract narrative structure from free text in real time. It features a colorful TUI with three panels:
- Left panel: Text entry area for user input
- Right top panel: Displays extracted narrative objects (people, places, events, relationships)
- Right bottom panel: Error messages

## Common Development Commands

### Running the Application
```bash
# Activate virtual environment
source venv/bin/activate

# Run with local Ollama model (default)
python main.py

# Run with OpenAI API (requires .env file with OPENAI_API_KEY)
python main.py --openai
```

### Testing
The project uses individual test scripts rather than a test framework:
```bash
# Test LLM connectivity and basic functionality
python test_llm.py

# Test the full pipeline integration
python test_full_pipeline.py

# Test TUI components
python test_tui.py

# Test debounce functionality
python test_debounce.py

# Test error handling
python test_error_handling.py

# Test both provider integrations
python test_providers.py
```

### Environment Setup
```bash
# Create virtual environment
python -m venv venv

# Install dependencies
pip install -r requirements.txt

# For OpenAI API support (optional)
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

## Architecture

### Core Components
- **LLMClient** (`llm_client.py`) - Handles Ollama API communication at localhost:11434 using gemma3:1b model
- **NarrativeParser** (`narrative_parser.py`) - Processes LLM JSON responses into structured objects
- **ObjectManager** (`object_manager.py`) - Maintains state and merges object lists across updates
- **TUI Application** (`tui_app.py`) - Textual-based three-panel interface with debounced input
- **Data Models** (`models.py`) - NarrativeObject, Relationship, and ObjectCollection classes

### Data Flow
1. User types in left panel (TextArea widget)
2. 2-second debounce timer triggers LLM call
3. Text sent to Ollama with structured prompt
4. JSON response parsed into NarrativeObject instances
5. ObjectManager merges new objects with existing state
6. Right panel updates with current object list
7. Errors displayed in bottom panel

### Key Implementation Details
- Uses Textual framework for TUI with CSS styling
- Debounced input handling prevents excessive LLM calls
- Objects identified by name, with descriptions/relationships updateable
- Comprehensive error handling for network failures, malformed responses
- Signal handlers for clean Control-C exit
- Mouse interaction disabled for cleaner CLI experience

## Development Workflow

This project follows a specific development approach outlined in README.md and PLAN.md:

1. **Planning Phase**: Detailed implementation plan created before coding
2. **Early LLM Testing**: Dedicated phase to verify local Ollama integration
3. **Incremental Development**: Phased approach with immediate testing
4. **Simplicity First**: Minimal, targeted changes affecting as little code as possible
5. **Commit Often**: Every batch of changes committed

## Dependencies

- `requests>=2.31.0` - HTTP client for Ollama API
- `textual>=0.41.0` - Modern TUI framework with rich styling
- `openai>=1.0.0` - OpenAI API client (optional)
- `python-dotenv>=1.0.0` - Environment variable loading (optional)
- Python 3.7+ with dataclasses, typing, asyncio

## LLM Integration

### Ollama (Default)
- **Server**: Ollama at localhost:11434
- **Model**: gemma3:1b (switched from originally planned gemma3:270m)
- **Usage**: `python main.py` (default)

### OpenAI API (Optional)
- **Model**: gpt-3.5-turbo (configurable via OPENAI_MODEL env var)
- **Setup**: Add OPENAI_API_KEY to .env file
- **Usage**: `python main.py --openai`

### Common Settings
- **Prompt**: Structured to extract JSON with objects containing name, description, relationships
- **Timeout**: 30 seconds for API calls
- **Temperature**: 0.1 for consistent responses (configurable via OPENAI_TEMPERATURE)

## Testing Strategy

Individual test scripts validate specific functionality:
- LLM connectivity and model responses
- JSON parsing and object creation
- Object merging and state management
- TUI rendering and input handling
- Error scenarios (network failures, malformed data)
- Real-time debounce behavior