from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
import logging

class SearchReplaceDialog(QDialog):
    """
    A dialog for searching and replacing text within the editor.
    """
    
    def __init__(self, text_edit, parent=None):
        """
        Initialize the SearchReplaceDialog.
        
        :param text_edit: QTextEdit - The text editor to perform search and replace on.
        :param parent: QWidget - The parent widget.
        """
        super().__init__(parent)
        self.text_edit = text_edit
        self.setWindowTitle("Search and Replace")
        self.init_ui()
    
    def init_ui(self):
        """
        Set up the user interface of the dialog.
        """
        layout = QVBoxLayout()
        
        # Search Field
        self.search_label = QLabel("Search:")
        self.search_input = QLineEdit()
        layout.addWidget(self.search_label)
        layout.addWidget(self.search_input)
        
        # Replace Field
        self.replace_label = QLabel("Replace with:")
        self.replace_input = QLineEdit()
        layout.addWidget(self.replace_label)
        layout.addWidget(self.replace_input)
        
        # Buttons
        self.search_button = QPushButton("Search")
        self.replace_button = QPushButton("Replace")
        self.replace_all_button = QPushButton("Replace All")
        layout.addWidget(self.search_button)
        layout.addWidget(self.replace_button)
        layout.addWidget(self.replace_all_button)
        
        # Connect Buttons
        self.search_button.clicked.connect(self.search_text)
        self.replace_button.clicked.connect(self.replace_text)
        self.replace_all_button.clicked.connect(self.replace_all_text)
        
        self.setLayout(layout)
    
    def search_text(self):
        """
        Search for the text in the editor.
        """
        search_term = self.search_input.text()
        if not search_term:
            QMessageBox.warning(self, "Warning", "Please enter text to search.")
            return
        cursor = self.text_edit.textCursor()
        document = self.text_edit.document()
        found = document.find(search_term, cursor)
        if found:
            self.text_edit.setTextCursor(found)
            logging.info(f"Search term '{search_term}' found.")
        else:
            QMessageBox.information(self, "Info", "No more occurrences found.")
            logging.info(f"Search term '{search_term}' not found.")
    
    def replace_text(self):
        """
        Replace the currently selected text.
        """
        cursor = self.text_edit.textCursor()
        if cursor.hasSelection():
            cursor.insertText(self.replace_input.text())
            self.search_text()
            logging.info("Replaced selected text.")
        else:
            self.search_text()
    
    def replace_all_text(self):
        """
        Replace all occurrences of the search term with the replacement text.
        """
        search_term = self.search_input.text()
        replace_term = self.replace_input.text()
        if not search_term:
            QMessageBox.warning(self, "Warning", "Please enter text to search.")
            return
        text = self.text_edit.toPlainText()
        new_text = text.replace(search_term, replace_term)
        self.text_edit.setPlainText(new_text)
        QMessageBox.information(self, "Info", f"All occurrences of '{search_term}' have been replaced with '{replace_term}'.")
        logging.info(f"Replaced all occurrences of '{search_term}' with '{replace_term}'.")
