#!/usr/bin/env python3
"""
Literate: A tool that extracts narrative structure from free text using LLM.
"""

from tui_app import LiterateApp

def main():
    """Main entry point for the Literate application."""
    app = LiterateApp()
    app.run()

if __name__ == "__main__":
    main()