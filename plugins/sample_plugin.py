# modules/input_validator.py

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
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if re.match(pattern, email):
            logging.info("Email validated successfully.")
            return True
        logging.warning("Invalid email format.")
        return False
