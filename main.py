#!/usr/bin/env python3
"""
Literate: A tool that extracts narrative structure from free text using LLM.
"""

import argparse
import sys
from tui_app import LiterateApp

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Literate - Extract narrative structure from text using LLM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Use local Ollama model (default)
  python main.py --openai          # Use OpenAI API (requires .env file with OPENAI_API_KEY)
        """
    )
    
    parser.add_argument(
        "--openai",
        action="store_true",
        help="Use OpenAI API instead of local Ollama model (requires OPENAI_API_KEY in .env file)"
    )
    
    return parser.parse_args()

def main():
    """Main entry point for the Literate application."""
    args = parse_args()
    
    # Determine LLM provider
    provider = "openai" if args.openai else "ollama"
    
    try:
        app = LiterateApp(llm_provider=provider)
        app.run()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()