# Standard library imports
import os
import sys
import threading
import asyncio
import hashlib
import base64
import logging
import json
import csv
import sqlite3
from datetime import datetime
from typing import Dict, Optional, Any, Tuple, List
from dataclasses import dataclass
from pathlib import Path

# Third-party imports
import openai
import pyttsx3
import requests
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTextEdit, QPushButton, QLabel,
    QCheckBox, QProgressBar, QMessageBox, QComboBox, QSpinBox, QAction,
    QFileDialog, QStatusBar, QGroupBox, QGridLayout, QHBoxLayout, QVBoxLayout,
    QInputDialog, QLineEdit, QDialog, QFormLayout, QDialogButtonBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject, QTimer, QSettings
from PyQt5.QtGui import QFont, QColor, QPalette, QTextCharFormat, QSyntaxHighlighter

# Local imports
from auth_dialogs import LoginDialog, RegisterDialog
