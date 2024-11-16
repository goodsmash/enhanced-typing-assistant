import openai
import logging

class GrammarEnhancer:
    """
    Enhances grammar and style of text using OpenAI's GPT-4 API.
    """
    
    def __init__(self, api_key: str):
        """
        Initialize the GrammarEnhancer with the provided OpenAI API key.
        
        :param api_key: str - OpenAI API key.
        """
        openai.api_key = api_key
        logging.info("GrammarEnhancer initialized with OpenAI API key.")
    
    def enhance_grammar(self, text: str) -> str:
        """
        Enhance grammar and style of the provided text.
        
        :param text: str - Text to enhance.
        :return: str - Enhanced text.
        """
        try:
            prompt = f"Improve the grammar and style of the following text while preserving its original meaning:\n\n{text}"
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=1000,
                temperature=0.5
            )
            enhanced_text = response.choices[0].text.strip()
            logging.info("Grammar enhanced successfully using OpenAI API.")
            return enhanced_text
        except openai.error.InvalidRequestError as e:
            logging.error(f"Invalid request to OpenAI API: {e}")
            return "Invalid request. Please check the input text."
        except openai.error.AuthenticationError as e:
            logging.error(f"Authentication error with OpenAI API: {e}")
            return "Authentication error. Please check your API key."
        except Exception as e:
            logging.error(f"Failed to enhance grammar: {e}")
            return "An error occurred during grammar enhancement."
