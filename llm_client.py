"""
LLM Client for communicating with Ollama API server.
"""
import json
import requests
from typing import Dict, List, Optional, Any
from models import NarrativeObject, Relationship
from narrative_parser import NarrativeParser


class LLMClient:
    """Client for interacting with Ollama API server."""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "gemma3:270m"):
        """
        Initialize the LLM client.
        
        Args:
            base_url: The base URL for the Ollama server
            model: The model name to use for generation
        """
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.timeout = 30  # seconds
        self.parser = NarrativeParser()
    
    def extract_narrative_objects(self, text: str) -> List[NarrativeObject]:
        """
        Extract narrative objects from the given text.
        
        Args:
            text: The input text to analyze
            
        Returns:
            List of NarrativeObject instances
            
        Raises:
            ConnectionError: If unable to connect to Ollama server
            ValueError: If response is not valid JSON or has unexpected format
        """
        if not text.strip():
            return []
        
        # Truncate very long texts to avoid token limits and parsing issues
        if len(text) > 2000:
            text = text[:2000] + "..."
        
        prompt = self._create_extraction_prompt(text)
        response = self._call_ollama(prompt)
        return self.parser.parse_llm_response(response.get("response", ""))
    
    def _create_extraction_prompt(self, text: str) -> str:
        """Create the prompt for narrative object extraction."""
        return f"""Analyze the following text and extract narrative objects (people, characters, places, events) and their relationships.

Return ONLY valid JSON in this exact format with no extra text:
{{
  "objects": [
    {{
      "name": "ObjectName",
      "description": "One sentence description.",
      "relationships": []
    }}
  ]
}}

Important rules:
- Only include objects clearly mentioned in the text
- Use actual object names for relationships, not "OtherObjectName"
- If no clear relationships exist, use empty relationships array
- Keep descriptions under 100 characters
- Return only the JSON, no markdown formatting

Text to analyze:
{text}"""
    
    def _call_ollama(self, prompt: str) -> Dict[str, Any]:
        """
        Make a request to the Ollama API.
        
        Args:
            prompt: The prompt to send to the model
            
        Returns:
            The API response as a dictionary
        """
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        try:
            response = requests.post(
                url, 
                json=payload, 
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(f"Failed to connect to Ollama server at {self.base_url}: {e}")
        except requests.exceptions.Timeout as e:
            raise ConnectionError(f"Request to Ollama server timed out after {self.timeout}s: {e}")
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Request to Ollama server failed: {e}")
    
    
    def test_connection(self) -> bool:
        """
        Test if the Ollama server is accessible.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            url = f"{self.base_url}/api/tags"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return True
        except Exception:
            return False