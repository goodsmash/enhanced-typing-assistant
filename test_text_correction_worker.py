import unittest
from unittest.mock import patch, MagicMock
from assistant_ui import TextCorrectionWorker, ExpiringCache

class TestTextCorrectionWorker(unittest.TestCase):

    @patch('assistant_ui.openai.ChatCompletion.create')
    def test_run_success(self, mock_chat_completion):
        # Arrange
        mock_chat_completion.return_value = MagicMock(
            choices=[MagicMock(message={'content': 'corrected text'})],
            usage={'total_tokens': 10}
        )
        worker = TextCorrectionWorker(
            text="This is a test.",
            mode="Standard",
            severity="High",
            language="en_US",
            api_key="test_api_key",
            cache=ExpiringCache()
        )
        worker.result_ready = MagicMock()  # Mock the result_ready signal

        # Act
        worker.run()

        # Assert
        self.assertEqual(worker.result_ready.emit.call_count, 1)
        self.assertEqual(worker.result_ready.emit.call_args[0][0], 'corrected text')

    @patch('assistant_ui.openai.ChatCompletion.create')
    def test_run_invalid_input(self, mock_chat_completion):
        # Arrange
        worker = TextCorrectionWorker(
            text="",
            mode="Standard",
            severity="High",
            language="en_US",
            api_key="test_api_key",
            cache=ExpiringCache()
        )
        worker.error_occurred = MagicMock()  # Mock the error_occurred signal

        # Act
        worker.run()

        # Assert
        self.assertEqual(worker.error_occurred.emit.call_count, 1)
        self.assertEqual(worker.error_occurred.emit.call_args[0][0], "Invalid input text.")

    @patch('assistant_ui.openai.ChatCompletion.create')
    def test_run_api_limit_exceeded(self, mock_chat_completion):
        # Arrange
        worker = TextCorrectionWorker(
            text="This is a test.",
            mode="Standard",
            severity="High",
            language="en_US",
            api_key="test_api_key",
            cache=ExpiringCache()
        )
        worker.check_api_limits = MagicMock(return_value=False)
        worker.error_occurred = MagicMock()  # Mock the error_occurred signal

        # Act
        worker.run()

        # Assert
        self.assertEqual(worker.error_occurred.emit.call_count, 1)
        self.assertEqual(worker.error_occurred.emit.call_args[0][0], "API usage limits exceeded.")

    @patch('assistant_ui.enchant.Dict')
    def test_spell_check_highlighter(self, mock_enchant):
        # Arrange
        mock_dict = MagicMock()
        mock_dict.check.return_value = False  # Simulate a misspelled word
        mock_enchant.return_value = mock_dict

        worker = TextCorrectionWorker(
            text="Ths is a tst.",
            mode="Standard",
            severity="High",
            language="en_US",
            api_key="test_api_key",
            cache=ExpiringCache()
        )

        # Act
        patterns = worker.analyze_typing_patterns(worker.text)

        # Assert
        self.assertIn('Ths', patterns['adjacent_errors'])
        self.assertIn('tst', patterns['repeats'])

    @patch('assistant_ui.openai.ChatCompletion.create')
    def test_run_fallback_to_local_correction(self, mock_chat_completion):
        # Arrange
        mock_chat_completion.side_effect = Exception("API error")
        worker = TextCorrectionWorker(
            text="This is a test.",
            mode="Standard",
            severity="High",
            language="en_US",
            api_key="test_api_key",
            cache=ExpiringCache()
        )
        worker.result_ready = MagicMock()  # Mock the result_ready signal

        # Act
        worker.run()

        # Assert
        self.assertEqual(worker.result_ready.emit.call_count, 1)
        self.assertIn("This is a test.", worker.result_ready.emit.call_args[0][0])

if __name__ == '__main__':
    unittest.main()
