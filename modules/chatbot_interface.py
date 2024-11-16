import openai
import logging

class ChatbotInterface:
    """
    Provides a chatbot interface for user assistance using OpenAI's GPT-4 API.
    """
    
    def __init__(self, api_key: str):
        """
        Initialize the ChatbotInterface with the provided OpenAI API key.
        
        :param api_key: str - OpenAI API key.
        """
        openai.api_key = api_key
        logging.info("ChatbotInterface initialized with OpenAI API key.")
    
    def get_response(self, user_input: str) -> str:
        """
        Get a response from the chatbot based on user input.
        
        :param user_input: str - User's message.
        :return: str - Chatbot's response.
        """
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.7,
                max_tokens=500
            )
            chatbot_response = response['choices'][0]['message']['content'].strip()
            logging.info("Chatbot responded successfully.")
            return chatbot_response
        except openai.error.InvalidRequestError as e:
            logging.error(f"Invalid request to OpenAI API: {e}")
            return "Invalid request. Please check your input."
        except openai.error.AuthenticationError as e:
            logging.error(f"Authentication error with OpenAI API: {e}")
            return "Authentication error. Please check your API key."
        except Exception as e:
            logging.error(f"Failed to get chatbot response: {e}")
            return "An error occurred while getting a response from the chatbot."
