import sqlite3
import logging
from typing import List, Tuple

class DatabaseManager:
    """
    Handles all database operations for the Typing Assistant.
    """
    
    def __init__(self, db_path='typing_assistant.db'):
        """
        Initialize the DatabaseManager by connecting to the SQLite database.
        
        :param db_path: str - Path to the SQLite database file.
        """
        self.db_path = db_path
        self.conn = self.connect_db()
        self.create_tables()
    
    def connect_db(self) -> sqlite3.Connection:
        """
        Connect to the SQLite database.
        
        :return: sqlite3.Connection - The database connection object.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            logging.info(f"Connected to SQLite database at '{self.db_path}'.")
            return conn
        except sqlite3.Error as e:
            logging.error(f"Failed to connect to database: {e}")
            return None
    
    def create_tables(self) -> None:
        """
        Create necessary tables if they do not exist.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS correction_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                input_text TEXT NOT NULL,
                corrected_text TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS clipboard_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                copied_text TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )''')
            self.conn.commit()
            logging.info("Database tables created or verified successfully.")
        except sqlite3.Error as e:
            logging.error(f"Failed to create tables: {e}")
    
    def close_db(self) -> None:
        """
        Close the database connection.
        """
        if self.conn:
            self.conn.close()
            logging.info("Database connection closed.")
    
    def add_user(self, username: str, password: str) -> bool:
        """
        Add a new user to the database.
        
        :param username: str - The username.
        :param password: str - The hashed password.
        :return: bool - True if added successfully, False otherwise.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            self.conn.commit()
            logging.info(f"User '{username}' added successfully.")
            return True
        except sqlite3.IntegrityError:
            logging.warning(f"User '{username}' already exists.")
            return False
        except sqlite3.Error as e:
            logging.error(f"Failed to add user '{username}': {e}")
            return False

    # Additional methods for managing corrections and clipboard history can be added here.
