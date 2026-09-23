"""
GROQ API Client Utility
Handles all interactions with the GROQ LLM API
"""
import json
import requests
from typing import List, Dict, Optional
from config.settings import GROQ_API_KEY, GROQ_BASE_URL, GROQ_MODEL


class GroqClient:
    """Client for interacting with GROQ API"""

    def __init__(self, api_key: str = GROQ_API_KEY, model: str = GROQ_MODEL):
        self.api_key = api_key
        self.model = model
        self.base_url = GROQ_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def chat_completion(
        self,
        messages: List[Dict],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Send a chat completion request to GROQ API
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response
            system_prompt: Optional system prompt to prepend
            
        Returns:
            Response text from the model
        """
        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + messages

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            raise Exception(f"GROQ API request failed: {str(e)}")
        except (KeyError, IndexError) as e:
            raise Exception(f"Failed to parse GROQ API response: {str(e)}")

    def simple_query(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Simple single-turn query
        
        Args:
            prompt: User prompt text
            system_prompt: Optional system context
            
        Returns:
            Model response text
        """
        messages = [{"role": "user", "content": prompt}]
        return self.chat_completion(messages, system_prompt=system_prompt)

    def structured_query(self, prompt: str, system_prompt: Optional[str] = None) -> Dict:
        """
        Query expecting JSON structured response
        
        Args:
            prompt: User prompt requesting JSON output
            system_prompt: Optional system context
            
        Returns:
            Parsed JSON dict
        """
        json_prompt = prompt + "\n\nRespond ONLY with valid JSON, no additional text."
        response = self.simple_query(json_prompt, system_prompt=system_prompt)
        
        # Extract JSON from response
        try:
            # Try direct parse first
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON block
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            # Try array
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            raise Exception(f"Could not parse JSON from response: {response[:200]}")

    def transcribe_audio(self, audio_file_path: str) -> str:
        """
        Transcribe audio using Whisper via GROQ
        
        Args:
            audio_file_path: Path to audio file
            
        Returns:
            Transcribed text
        """
        from config.settings import WHISPER_MODEL
        
        with open(audio_file_path, "rb") as audio_file:
            files = {"file": audio_file}
            data = {"model": WHISPER_MODEL}
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            response = requests.post(
                f"{self.base_url}/audio/transcriptions",
                headers=headers,
                files=files,
                data=data,
                timeout=120
            )
            response.raise_for_status()
            return response.json().get("text", "")
