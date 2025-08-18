# Implementation Plan for Literate

## Project Overview
Build a Python TUI application that extracts narrative objects from free text using a local LLM (Ollama with gemma3:270m), featuring real-time text analysis with a 3-second debounce mechanism.

## System Architecture

### Core Components
1. **LLM Client** - Handles Ollama API communication
2. **Narrative Parser** - Processes LLM responses into structured objects
3. **Object Manager** - Maintains state and merges object lists
4. **TUI Controller** - Manages the three-panel interface
5. **Text Input Handler** - Manages debounced text input
6. **Main Application** - Coordinates all components

### Data Models
- **NarrativeObject**: name, description, relationships
- **Relationship**: target_object, description
- **APIResponse**: structured LLM response schema

## Implementation Tasks

### Phase 1: Environment Setup and LLM Integration Testing ✅ = Complete
- [x] 1.1: Set up Python virtual environment
- [x] 1.2: Create basic project structure (main.py, requirements.txt)
- [x] 1.3: Install initial dependencies (requests, typing)
- [x] 1.4: Create LLM client class for Ollama API calls
- [x] 1.5: Design and test LLM prompt for narrative extraction
- [x] 1.6: Test basic LLM connectivity and response parsing
- [x] 1.7: Handle LLM errors and timeouts gracefully
- [x] 1.8: Validate that gemma3:270m model returns expected JSON schema

### Phase 2: Data Models and Object Management
- [x] 2.1: Define NarrativeObject and Relationship data classes
- [x] 2.2: Create JSON schema for LLM response validation
- [x] 2.3: Implement narrative object parser from LLM responses
- [x] 2.4: Build object manager for state persistence
- [x] 2.5: Implement object merging logic (add, remove, update)
- [x] 2.6: Test object merging with various scenarios
- [x] 2.7: Add comprehensive error handling for malformed responses

### Phase 3: TUI Framework Setup
- [x] 3.1: Research and select TUI library (Rich, Textual, or similar)
- [x] 3.2: Install TUI dependencies
- [x] 3.3: Create basic three-panel layout structure
- [x] 3.4: Implement text input panel with cursor management
- [x] 3.5: Create object display panel with formatting
- [x] 3.6: Add small error message panel
- [x] 3.7: Test basic TUI rendering and layout responsiveness

### Phase 4: Input Handling and Debouncing ✅ = Complete
- [x] 4.1: Implement text input capture and buffering
- [x] 4.2: Create 3-second debounce timer mechanism
- [x] 4.3: Handle paste operations properly
- [x] 4.4: Add text editing capabilities (backspace, cursor movement)
- [x] 4.5: Test debounce behavior with various input patterns
- [x] 4.6: Ensure input doesn't block TUI rendering

### Phase 5: Integration and Real-time Updates ✅ = Complete
- [x] 5.1: Connect text input to LLM processing pipeline
- [x] 5.2: Integrate object manager with TUI display updates
- [x] 5.3: Add loading indicators during LLM calls
- [x] 5.4: Implement error display in bottom panel
- [x] 5.5: Test full pipeline: input → debounce → LLM → parse → display
- [x] 5.6: Handle edge cases (empty input, network failures)

### Phase 6: Polish and Error Handling ✅ = Complete
- [x] 6.1: Add colorful styling to TUI panels
- [x] 6.2: Implement proper Control-C exit handling
- [x] 6.3: Add animation/transitions for object updates
- [x] 6.4: Comprehensive error message improvements
- [x] 6.5: Performance optimization for large text inputs
- [x] 6.6: Final testing with various text types and scenarios

### Phase 7: Documentation and Packaging
- [ ] 7.1: Create requirements.txt with pinned versions
- [ ] 7.2: Add usage instructions to README
- [ ] 7.3: Create example text samples for testing
- [ ] 7.4: Final integration testing
- [ ] 7.5: Code cleanup and documentation

## Testing Strategy

### Early Testing Priorities
1. **LLM Connectivity**: Verify Ollama is accessible at localhost:11434
2. **Model Response**: Confirm gemma3:270m returns structured JSON
3. **Prompt Engineering**: Test prompt produces consistent object extraction
4. **Error Scenarios**: Network failures, malformed responses, timeouts

### Integration Testing
- Text input → LLM processing → Object parsing → TUI display
- Object state management across multiple LLM calls
- Debounce timing under various input patterns
- Memory usage with large object lists

### Manual Testing Scenarios
- Short narratives (1-2 sentences)
- Long texts with many characters/places
- Technical documentation (should extract few objects)
- Fiction with complex relationships
- Empty/whitespace-only input

## Technical Decisions

### LLM Prompt Design
Create a prompt that instructs the LLM to return a JSON array with objects containing:
```json
{
  "objects": [
    {
      "name": "ObjectName",
      "description": "One sentence description",
      "relationships": [
        {
          "target": "OtherObjectName", 
          "description": "One sentence relationship"
        }
      ]
    }
  ]
}
```

### TUI Library Selection
Evaluate options based on:
- Three-panel layout support
- Real-time input handling
- Color and animation capabilities
- Text editing features
- Performance with frequent updates

### Error Handling Philosophy
- Never crash the application
- Display helpful error messages to user
- Log technical details for debugging
- Graceful degradation when LLM unavailable

## Dependencies
- `requests` - HTTP client for Ollama API
- `typing` - Type hints support
- TUI library (TBD in Phase 3)
- `dataclasses` or `pydantic` - Data models
- `json` - Response parsing
- `threading` or `asyncio` - Debounce timing

## Success Criteria
- [ ] Application starts without errors
- [ ] Successfully connects to Ollama and processes text
- [ ] TUI displays three panels correctly
- [ ] Real-time text processing with 3-second debounce
- [ ] Object state persists and merges correctly
- [ ] Graceful error handling and user feedback
- [ ] Clean exit with Control-C