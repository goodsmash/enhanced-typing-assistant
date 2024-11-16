import pyperclip
import logging
from typing import List, Tuple
from modules.database_manager import DatabaseManager

class ClipboardManager:
    """
    Manages clipboard operations and maintains a history of copied texts.
    """
    
    def __init__(self, db_manager: DatabaseManager, user_id: int, history_limit: int = 50):
        """
        Initialize the ClipboardManager.
        
        :param db_manager: DatabaseManager - Instance of DatabaseManager.
        :param user_id: int - The current user's ID.
        :param history_limit: int - Maximum number of history entries.
        """
        self.db_manager = db_manager
        self.user_id = user_id
        self.history_limit = history_limit
        logging.info("ClipboardManager initialized.")
    
    def copy_to_clipboard(self, text: str) -> None:
        """
        Copy text to the clipboard and add to history.
        
        :param text: str - Text to copy.
        """
        try:
            pyperclip.copy(text)
            self.db_manager.add_clipboard_history(self.user_id, text)
            logging.info("Text copied to clipboard and history updated.")
        except Exception as e:
            logging.error(f"Failed to copy to clipboard: {e}")
    
    def paste_from_clipboard(self) -> str:
        """
        Paste text from the clipboard.
        
        :return: str - Text from clipboard.
        """
        try:
            text = pyperclip.paste()
            logging.info("Text pasted from clipboard.")
            return text
        except Exception as e:
            logging.error(f"Failed to paste from clipboard: {e}")
            return ""
    
    def get_history(self) -> List[Tuple[str, str]]:
        """
        Retrieve clipboard history.
        
        :return: List[Tuple[str, str]] - List of copied texts and timestamps.
        """
        try:
            history = self.db_manager.get_clipboard_history(self.user_id)
            logging.info("Clipboard history retrieved successfully.")
            return history
        except Exception as e:
            logging.error(f"Failed to retrieve clipboard history: {e}")
            return []
    
    def clear_history(self) -> None:
        """
        Clear clipboard history.
        """
        try:
            self.db_manager.cursor.execute('DELETE FROM clipboard_history WHERE user_id=?', (self.user_id,))
            self.db_manager.conn.commit()
            logging.info("Clipboard history cleared.")
        except Exception as e:
            logging.error(f"Failed to clear clipboard history: {e}")
