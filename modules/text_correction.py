import openai
import logging
from typing import Dict

class TextCorrection:
    """
    Handles text correction using OpenAI's GPT-4 API.
    """
    
    def __init__(self, api_key: str):
        """
        Initialize the TextCorrection with the provided OpenAI API key.
        
        :param api_key: str - OpenAI API key.
        """
        openai.api_key = api_key
        logging.info("TextCorrection initialized with OpenAI API key.")
    
    def correct_text(self, text: str, mode: str) -> str:
        """
        Correct the provided text based on the selected mode.
        
        :param text: str - The text to be corrected.
        :param mode: str - Correction mode ('Basic' or 'Advanced').
        :return: str - Corrected text.
        """
        try:
            if mode == 'Basic':
                prompt = f"Correct the following text for grammar and spelling errors:\n\n{text}"
            elif mode == 'Advanced':
                prompt = f"Provide an advanced correction of the following text, improving clarity and style:\n\n{text}"
            else:
                prompt = f"Correct the following text:\n\n{text}"
            
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=1000,
                temperature=0.5
            )
            
            corrected_text = response.choices[0].text.strip()
            logging.info("Text corrected successfully using OpenAI API.")
            return corrected_text
        except openai.error.InvalidRequestError as e:
            logging.error(f"Invalid request to OpenAI API: {e}")
            return "Invalid request. Please check the input text."
        except openai.error.AuthenticationError as e:
            logging.error(f"Authentication error with OpenAI API: {e}")
            return "Authentication error. Please check your API key."
        except Exception as e:
            logging.error(f"Failed to correct text: {e}")
            return "An error occurred during text correction."
