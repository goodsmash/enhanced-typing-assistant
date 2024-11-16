import os
from cryptography.fernet import Fernet
import logging
from dotenv import load_dotenv

class APIManager:
    """
    Manages API keys and secure access to external services.
    """
    
    def __init__(self, key_file='key.key'):
        """
        Initialize the APIManager, loading the encryption key and environment variables.
        
        :param key_file: str - Path to the encryption key file.
        """
        self.key_file = key_file
        self.key = self.load_key()
        self.fernet = Fernet(self.key) if self.key else None
        load_dotenv()  # Load environment variables from .env file
        logging.info("APIManager initialized.")
    
    def load_key(self):
        """
        Load the encryption key from the key file.
        
        :return: bytes - The encryption key.
        """
        if not os.path.exists(self.key_file):
            logging.error(f"Encryption key file '{self.key_file}' not found.")
            return None
        try:
            with open(self.key_file, 'rb') as file:
                key = file.read()
            logging.info("Encryption key loaded successfully.")
            return key
        except Exception as e:
            logging.error(f"Failed to load encryption key: {e}")
            return None
    
    def encrypt_api_key(self, api_key: str) -> str:
        """
        Encrypt the API key.
        
        :param api_key: str - The API key to encrypt.
        :return: str - The encrypted API key.
        """
        if not self.fernet:
            logging.error("Fernet not initialized. Cannot encrypt API key.")
            return ""
        encrypted = self.fernet.encrypt(api_key.encode()).decode()
        logging.info("API key encrypted successfully.")
        return encrypted
    
    def decrypt_api_key(self, encrypted_api_key: str) -> str:
        """
        Decrypt the API key.
        
        :param encrypted_api_key: str - The encrypted API key.
        :return: str - The decrypted API key.
        """
        if not self.fernet:
            logging.error("Fernet not initialized. Cannot decrypt API key.")
            return ""
        try:
            decrypted = self.fernet.decrypt(encrypted_api_key.encode()).decode()
            logging.info("API key decrypted successfully.")
            return decrypted
        except Exception as e:
            logging.error(f"Failed to decrypt API key: {e}")
            return ""
    
    def get_openai_api_key(self) -> str:
        """
        Retrieve the OpenAI API key from environment variables.
        
        :return: str - The decrypted OpenAI API key.
        """
        encrypted_key = os.getenv('OPENAI_API_KEY_ENCRYPTED')
        if encrypted_key:
            return self.decrypt_api_key(encrypted_key)
        else:
            logging.error("OpenAI API key not found in environment variables.")
            return ""
    
    def set_openai_api_key(self, api_key: str) -> bool:
        """
        Set the OpenAI API key by encrypting and storing it in environment variables.
        
        :param api_key: str - The OpenAI API key to set.
        :return: bool - True if successful, False otherwise.
        """
        encrypted_key = self.encrypt_api_key(api_key)
        if encrypted_key:
            try:
                with open('.env', 'a') as env_file:
                    env_file.write(f"\nOPENAI_API_KEY_ENCRYPTED={encrypted_key}\n")
                logging.info("OpenAI API key set successfully.")
                return True
            except Exception as e:
                logging.error(f"Failed to set OpenAI API key in .env: {e}")
                return False
        return False
