import matplotlib.pyplot as plt
import logging
from modules.database_manager import DatabaseManager
from typing import List, Tuple

class DataVisualizer:
    """
    Visualizes user data such as clipboard history using Matplotlib.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize the DataVisualizer with the DatabaseManager instance.
        
        :param db_manager: DatabaseManager - Instance of DatabaseManager.
        """
        self.db_manager = db_manager
        logging.info("DataVisualizer initialized.")
    
    def plot_clipboard_history(self, user_id: int) -> None:
        """
        Plot the clipboard history over time.
        
        :param user_id: int - The user's ID.
        """
        try:
            history = self.db_manager.get_clipboard_history(user_id)
            if not history:
                logging.warning("No clipboard history to visualize.")
                return
            texts, timestamps = zip(*history)
            counts = list(range(1, len(texts) + 1))
            
            plt.figure(figsize=(10, 6))
            plt.plot(timestamps, counts, marker='o', linestyle='-')
            plt.title('Clipboard History Over Time')
            plt.xlabel('Timestamp')
            plt.ylabel('Number of Copies')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()
            logging.info("Clipboard history visualized successfully.")
        except ValueError as e:
            logging.error(f"Value error during visualization: {e}")
        except Exception as e:
            logging.error(f"Failed to visualize clipboard history: {e}")
