#!/usr/bin/env python3
"""
Debug script to see raw LLM responses.
"""
from llm_client import LLMClient

def debug_raw_response():
    """Debug what the LLM is actually returning."""
    client = LLMClient()
    
    test_text = "Alice met Bob at the coffee shop."
    prompt = client._create_extraction_prompt(test_text)
    
    print("=== PROMPT ===")
    print(prompt)
    print("\n=== RAW RESPONSE ===")
    
    try:
        response = client._call_ollama(prompt)
        print("Full response:")
        print(response)
        print(f"\nResponse text: '{response.get('response', '')}'")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_raw_response()