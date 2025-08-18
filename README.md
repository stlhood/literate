# Literate

## Overview
Literate is a tool that uses a locally-running LLM to extract meaning and structure from user-entered free text in real time. It runs from the command-line and utilizes a colorful TUI.

## Functionality
- The user types or pastes text into an entry area.
- After the user has typed or pasted new text into the entry area, the system waits 3 seconds to see if they are still entering text. If no further text is entered during that time, then the system makes a call to a locally-running LLM.
- The user-entered text is sent to the LLM, with a prompt that instructs the LLM to process the text in its entirety and extract a list of people, characters, places, events and other narrative objects that exist within the text. Each object should have a short (1 sentence) description. If an object has a narrative relationship to one or more other objects, then one of those relationships should also be described with a single sentence that names the object with which there is a relationship.
- The LLM should return this list of narrative objects according to a consistent, pre-defined schema that our program is designed to understand.
- If the LLM does not respond or if there is an error, a useful error message is displayed.
- When the program receives the LLM's response, it process the list and displays it, nicely-formatted.
- When the user types or pastes-in more text, the LLM process repeats.
- However, the program maintains in memory a list of all narrative objects previously recorded. Each time the LLM is called and a new list of objects is returned, it only updates the displayed list in specific ways:
    - Any new objects are added to the displayed list.
    - Any objects that hav been deleted are removed from the displayed list.
    - Any objects that were previously displayed are left unchanged in name, but their description and/or relatonship can be updated.

## Interface
- The interface is a colorful TUI comprised of three panels.
- The left half of the screen is a text entry area, where the user can type or paste whatever text they want.
- The right half of the screen has two vertically-stacked panels.
    - The top panel fills the top 4/5 of the screen and displays the list of narrative objects received from the LLM and maintianed by the program.
    - The bottom panel is very small and is onl used to display error mesages when they occur.
- The program can be exited with a Control-C.
- Other than typing or pasting text into the left panel, there is no other user interaction.

## Architecture and implementation
- Overall system: Literate is built in Python and invoked via the command line.
- LLM: the program calls a locally-running LLM. It is served by Ollama using Ollama's OpenAI-compatible API server, running at localhost:11434. The model to use is gemma3:270m.
- TUI: Use a popular TUI library that supports the functionality and interface described above, and enables a colorful and animated interface.

## How to build this project
- First read README.md, ultrathink through the problem, and write a plan to PLAN.md.
- Before you begin working, check in with me and I will verify the plan.
- Then, begin working on the todo items in order, marking them as complete in PLAN.md (and maintaining an updated implementation log) as you go.
- For any code that you write, immediately test it before proceeding. Fix any issues that arise during testing.
- At every step of the way give me a high level explanation of what changes you made.
- Make every task and code change you do as simple as possible. We want to avoid making any massive or complex changes. Every change should impact as little code as possible. Everything is about simplicity.
- Commit every batch of changes as you go.
- Do not commit any node modules to git.
- Use Python best practices and tools, like venv.
- Be sure to have a separate early phase of development that is just about making sure the local LLM is working, responding to calls, and returning results.
