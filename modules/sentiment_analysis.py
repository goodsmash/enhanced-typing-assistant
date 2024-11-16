import openai
import logging

class SentimentAnalyzer:
    """
    Analyzes the sentiment of text using OpenAI's GPT-4 API.
    """
    
    def __init__(self, api_key: str):
        """
        Initialize the SentimentAnalyzer with the provided OpenAI API key.
        
        :param api_key: str - OpenAI API key.
        """
        openai.api_key = api_key
        logging.info("SentimentAnalyzer initialized with OpenAI API key.")
    
    def analyze_sentiment(self, text: str) -> str:
        """
        Analyze the sentiment of the provided text.
        
        :param text: str - Text to analyze.
        :return: str - Sentiment result.
        """
        try:
            prompt = f"Analyze the sentiment of the following text and categorize it as Positive, Negative, or Neutral:\n\n{text}"
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=60,
                temperature=0.3
            )
            sentiment = response.choices[0].text.strip()
            logging.info("Sentiment analysis completed successfully.")
            return sentiment
        except openai.error.InvalidRequestError as e:
            logging.error(f"Invalid request to OpenAI API: {e}")
            return "Invalid request. Please check the input text."
        except openai.error.AuthenticationError as e:
            logging.error(f"Authentication error with OpenAI API: {e}")
            return "Authentication error. Please check your API key."
        except Exception as e:
            logging.error(f"Failed to analyze sentiment: {e}")
            return "An error occurred during sentiment analysis."
