import openai
import logging
from typing import Optional

class AISuggestions:
    """
    Provides AI-driven suggestions to improve writing using OpenAI's GPT-4 API.
    """
    
    def __init__(self, api_key: str):
        """
        Initialize the AISuggestions with the provided OpenAI API key.
        
        :param api_key: str - OpenAI API key.
        """
        openai.api_key = api_key
        logging.info("AISuggestions initialized with OpenAI API key.")
    
    def get_suggestions(self, text: str) -> str:
        """
        Get AI-driven suggestions to improve the provided text.
        
        :param text: str - The text to improve.
        :return: str - AI suggestions.
        """
        try:
            prompt = f"Provide constructive suggestions to improve the following text:\n\n{text}"
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=500,
                temperature=0.5
            )
            suggestions = response.choices[0].text.strip()
            logging.info("AI suggestions retrieved successfully.")
            return suggestions
        except openai.error.InvalidRequestError as e:
            logging.error(f"Invalid request to OpenAI API: {e}")
            return "Invalid request. Please check the input text."
        except openai.error.AuthenticationError as e:
            logging.error(f"Authentication error with OpenAI API: {e}")
            return "Authentication error. Please check your API key."
        except Exception as e:
            logging.error(f"Failed to get AI suggestions: {e}")
            return "An error occurred while fetching suggestions."
