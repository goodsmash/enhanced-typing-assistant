import re
import logging

class InputValidator:
    """
    Validates and sanitizes user inputs.
    """
    
    @staticmethod
    def sanitize_text(text: str) -> str:
        """
        Sanitize the input text by removing potentially harmful characters.
        
        :param text: str - The text to sanitize.
        :return: str - Sanitized text.
        """
        if not isinstance(text, str):
            logging.error("Input for sanitization is not a string.")
            return ""
        
        sanitized = re.sub(r'[^\w\s.,!?\'"-]', '', text)
        logging.info("Input text sanitized.")
        return sanitized
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate the format of an email address.
        
        :param email: str - The email address to validate.
        :return: bool - True if valid, False otherwise.
        """
        if not isinstance(email, str):
            logging.error("Input for email validation is not a string.")
            return False
        
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if re.match(pattern, email):
            logging.info("Email validated successfully.")
            return True
        logging.warning("Invalid email format.")
        return False
