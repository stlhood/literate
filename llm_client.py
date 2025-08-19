"""
LLM Client for communicating with Ollama API server or OpenAI API.
"""
import json
import os
import requests
from typing import Dict, List, Optional, Any
from models import NarrativeObject, Relationship
from narrative_parser import NarrativeParser

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional


class LLMClient:
    """Client for interacting with Ollama API server or OpenAI API."""
    
    def __init__(self, provider: str = "ollama", base_url: str = "http://localhost:11434", 
                 model: str = None, temperature: float = 0.1):
        """
        Initialize the LLM client.
        
        Args:
            provider: "ollama" or "openai"
            base_url: The base URL for the Ollama server (ignored for OpenAI)
            model: The model name to use for generation
            temperature: Sampling temperature (0.0-1.0, lower = more deterministic)
        """
        self.provider = provider.lower()
        self.temperature = temperature
        self.timeout = 30  # seconds
        self.parser = NarrativeParser()
        
        if self.provider == "openai":
            try:
                import openai
                self.openai_client = openai
            except ImportError:
                raise ImportError("OpenAI library not installed. Run: pip install openai")
            
            # Set up OpenAI configuration
            self.api_key = os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables. Please set it in .env file.")
            
            self.model = model or os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
            self.temperature = float(os.getenv("OPENAI_TEMPERATURE", temperature))
            
            # Initialize OpenAI client
            self.client = openai.OpenAI(api_key=self.api_key)
            
        else:  # ollama
            self.base_url = base_url.rstrip('/')
            self.model = model or "gemma3:1b"
    
    def extract_narrative_objects(self, text: str) -> List[NarrativeObject]:
        """
        Extract narrative objects from the given text.
        
        Args:
            text: The input text to analyze
            
        Returns:
            List of NarrativeObject instances
            
        Raises:
            ConnectionError: If unable to connect to LLM provider
            ValueError: If response is not valid JSON or has unexpected format
        """
        if not text.strip():
            return []
        
        # Truncate very long texts to avoid token limits and parsing issues
        if len(text) > 2000:
            text = text[:2000] + "..."
        
        prompt = self._create_extraction_prompt(text)
        
        if self.provider == "openai":
            response = self._call_openai(prompt)
        else:
            response = self._call_ollama(prompt)
            response = response.get("response", "")
        
        return self.parser.parse_llm_response(response)
    
    def _create_extraction_prompt(self, text: str) -> str:
        """Create the prompt for narrative object extraction."""
        return f"""Extract narrative objects ONLY from this text. Do not add any objects not explicitly mentioned.

Text: "{text}"

Return valid JSON with this structure:
{{
  "objects": [
    {{
      "name": "string",
      "description": "string", 
      "relationships": []
    }}
  ]
}}

STRICT RULES:
- ONLY extract entities with specific names mentioned in the text
- Do NOT extract unnamed people (like "the detective", "a woman", "someone")
- Do NOT invent names for unnamed characters or objects
- Use exact names from text (e.g., if text says "Alice", use "Alice")
- If a person/thing has no name in the text, skip it entirely
- Descriptions must only state facts from the text
- Never use generic names like "person", "object", "character", "detective"

Return only the JSON:"""
    
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
            "stream": False,
            "options": {
                "temperature": self.temperature,  # Configurable temperature
                "top_k": 10,         # Limit to top 10 most likely tokens
                "top_p": 0.3,        # Use nucleus sampling with low probability mass
                "repeat_penalty": 1.1,  # Slight penalty for repetition
                "num_predict": 500   # Limit response length
            }
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
    
    def _call_openai(self, prompt: str) -> str:
        """
        Make a request to the OpenAI API.
        
        Args:
            prompt: The prompt to send to the model
            
        Returns:
            The response text from the model
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that extracts narrative objects from text. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=500,
                timeout=self.timeout
            )
            return response.choices[0].message.content
            
        except Exception as e:
            if "rate_limit" in str(e).lower():
                raise ConnectionError(f"OpenAI API rate limit exceeded: {e}")
            elif "authentication" in str(e).lower() or "unauthorized" in str(e).lower():
                raise ConnectionError(f"OpenAI API authentication failed. Check your API key: {e}")
            elif "timeout" in str(e).lower():
                raise ConnectionError(f"OpenAI API request timed out after {self.timeout}s: {e}")
            else:
                raise ConnectionError(f"OpenAI API request failed: {e}")
    
    def correct_narrative_object(self, original_object_name: str, full_text: str) -> Optional[NarrativeObject]:
        """
        Ask LLM to correct a specific narrative object.
        
        Args:
            original_object_name: Name of the object to correct
            full_text: The full original text for context
            
        Returns:
            Single corrected NarrativeObject or None if failed
        """
        if not full_text.strip():
            return None
        
        # Create correction prompt
        prompt = self._create_correction_prompt(original_object_name, full_text)
        
        if self.provider == "openai":
            response = self._call_openai(prompt)
        else:
            response = self._call_ollama(prompt)
            response = response.get("response", "")
        
        # Parse response expecting single object
        objects = self.parser.parse_llm_response(response)
        
        # Return the first (and should be only) object
        return objects[0] if objects else None
    
    def _create_correction_prompt(self, object_name: str, full_text: str) -> str:
        """Create prompt for correcting a specific narrative object."""
        return f"""The narrative object "{object_name}" extracted from this text needs correction.

Original text: "{full_text}"

The object "{object_name}" is incorrect, incomplete, or inaccurate in some way. 
Please provide a SINGLE corrected narrative object that better represents what should be extracted from this text.

Return ONLY valid JSON with exactly ONE object:
{{
  "objects": [
    {{
      "name": "CorrectedName",
      "description": "Accurate description based on the text", 
      "relationships": []
    }}
  ]
}}

RULES:
- Provide exactly ONE corrected object
- Use a more accurate name if the original was wrong
- Write a better description based on the actual text
- Only include relationships that are clearly mentioned
- Base everything strictly on the provided text

JSON response:"""
    
    def test_connection(self) -> bool:
        """
        Test if the LLM provider is accessible.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            if self.provider == "openai":
                # Test OpenAI connection with a simple completion
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=1,
                    timeout=5
                )
                return response.choices[0].message.content is not None
            else:
                # Test Ollama connection
                url = f"{self.base_url}/api/tags"
                response = requests.get(url, timeout=5)
                response.raise_for_status()
                return True
        except Exception:
            return False