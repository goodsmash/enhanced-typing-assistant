"""API client for handling OpenAI and other external service interactions."""

import logging
import time
from typing import Dict, Any, Optional

import openai
import requests

logger = logging.getLogger(__name__)

class APIClient:
    """Handles API interactions with rate limiting and error handling."""
    
    def __init__(self, api_key: str, **kwargs):
        """Initialize API client with settings."""
        self.api_key = api_key
        self.settings = kwargs
        self.last_call = 0
        self.min_delay = 1.0  # Minimum delay between API calls
        
        # Initialize OpenAI client
        openai.api_key = api_key
        
    def call_api(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make an API call with rate limiting and error handling."""
        # Enforce rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_call
        if time_since_last < self.min_delay:
            time.sleep(self.min_delay - time_since_last)
        
        try:
            # Make API call
            response = requests.post(
                f"https://api.openai.com/v1/{endpoint}",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json=data
            )
            response.raise_for_status()
            self.last_call = time.time()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API call failed: {e}")
            raise
            
    def process_text(self, text: str, mode: str = "correction") -> Dict[str, Any]:
        """Process text using the OpenAI API."""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self._get_system_prompt(mode)},
                    {"role": "user", "content": text}
                ],
                temperature=0.7,
                max_tokens=150,
                n=1
            )
            return {
                "success": True,
                "result": response.choices[0].message.content,
                "model": response.model
            }
            
        except Exception as e:
            logger.error(f"Text processing failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
            
    def _get_system_prompt(self, mode: str) -> str:
        """Get the appropriate system prompt based on the mode."""
        prompts = {
            "correction": "You are a helpful assistant that corrects spelling and grammar while preserving the original meaning.",
            "enhancement": "You are a helpful assistant that enhances text to make it more clear and professional while preserving the core message.",
            "simplification": "You are a helpful assistant that simplifies text to make it easier to understand while preserving the main points."
        }
        return prompts.get(mode, prompts["correction"])
        
    def check_api_key(self) -> bool:
        """Check if the API key is valid."""
        try:
            openai.Model.list()
            return True
        except:
            return False
