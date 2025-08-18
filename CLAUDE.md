# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Literate is a Python-based command-line tool that uses a locally-running LLM to extract narrative structure from free text in real time. It features a colorful TUI with three panels:
- Left panel: Text entry area for user input
- Right top panel: Displays extracted narrative objects (people, places, events, relationships)
- Right bottom panel: Error messages

## Architecture

- **Language**: Python
- **LLM Integration**: Ollama's OpenAI-compatible API server at localhost:11434 using gemma3:270m model
- **Interface**: TUI library for colorful, animated interface
- **Text Processing**: 3-second debounce after text input before LLM call
- **State Management**: Maintains persistent list of narrative objects, merging new extractions with existing data

## Development Workflow

This project follows a specific development approach outlined in README.md:

1. **Planning Phase**: Create detailed plan in PLAN.md before implementation
2. **Early LLM Testing**: Dedicated phase to verify local LLM integration works
3. **Incremental Development**: Work through todo items in PLAN.md, marking complete as you go
4. **Test-Driven**: Test every code change immediately before proceeding
5. **Simplicity First**: Make minimal, targeted changes affecting as little code as possible
6. **Commit Often**: Commit every batch of changes

## Python Environment

- Use virtual environments (venv) following Python best practices
- Do not commit any dependencies to git
- The project currently has no Python files - this is a greenfield implementation

## Key Implementation Notes

- The LLM receives user text with a prompt to extract narrative objects according to a predefined schema
- Objects have: name, 1-sentence description, and optional relationship to other objects
- The system performs intelligent merging of new and existing objects:
  - Add new objects
  - Remove deleted objects  
  - Update descriptions/relationships while preserving object names
- Error handling for LLM failures with useful user messages
- Exit with Control-C

## Testing Strategy

Since this involves real-time LLM integration, early testing of the Ollama connection and response parsing is critical before building the TUI components.