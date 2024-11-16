import pytest
from PyQt5.QtWidgets import QApplication
import sys

@pytest.fixture(scope="session")
def qapp():
    """Create a QApplication instance for the entire test session."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app
    app.quit()

@pytest.fixture
def mock_openai(monkeypatch):
    """Mock OpenAI API responses."""
    class MockResponse:
        def __init__(self, text):
            self.text = text
            self.choices = [type('Choice', (), {'text': text})]()

    def mock_completion(*args, **kwargs):
        return MockResponse("Mocked response")

    monkeypatch.setattr("openai.Completion.create", mock_completion)
    return mock_completion

@pytest.fixture
def temp_db_path(tmp_path):
    """Create a temporary database path."""
    return tmp_path / "test_typing_assistant.db"

@pytest.fixture
def mock_tts(monkeypatch):
    """Mock text-to-speech functionality."""
    class MockTTS:
        def say(self, text): pass
        def runAndWait(self): pass
        def stop(self): pass
        def getProperty(self, prop): return 1
        def setProperty(self, prop, val): pass

    monkeypatch.setattr("pyttsx3.init", lambda: MockTTS())
    return MockTTS()
