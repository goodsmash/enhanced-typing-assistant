import speech_recognition as sr
import logging

class SpeechToText:
    """
    Handles speech-to-text functionalities using SpeechRecognition.
    """
    
    def __init__(self, language: str = 'en-US'):
        """
        Initialize the SpeechToText with the specified language.
        
        :param language: str - Language code for speech recognition.
        """
        if sr:
            self.recognizer = sr.Recognizer()
            self.language = language
            logging.info(f"SpeechToText initialized with language: {language}")
        else:
            logging.error("SpeechRecognition is not installed.")
            self.recognizer = None
    
    def transcribe_audio(self, audio_file: str) -> str:
        """
        Transcribe the provided audio file to text.
        
        :param audio_file: str - Path to the audio file.
        :return: str - Transcribed text.
        """
        if not self.recognizer:
            logging.error("Speech recognizer not initialized.")
            return "Speech recognizer not available."
        
        try:
            with sr.AudioFile(audio_file) as source:
                audio = self.recognizer.record(source)
            text = self.recognizer.recognize_google(audio, language=self.language)
            logging.info(f"Audio transcribed successfully from file: {audio_file}")
            return text
        except sr.UnknownValueError:
            logging.error("Google Speech Recognition could not understand audio.")
            return "Speech could not be understood."
        except sr.RequestError as e:
            logging.error(f"Could not request results from Google Speech Recognition service; {e}")
            return "Speech Recognition service error."
        except Exception as e:
            logging.error(f"An unexpected error occurred during transcription: {e}")
            return "An unexpected error occurred."
    
    def capture_voice(self) -> str:
        """
        Capture voice input from the microphone and transcribe it to text.
        
        :return: str - Transcribed text.
        """
        if not self.recognizer:
            logging.error("Speech recognizer not initialized.")
            return "Speech recognizer not available."
        
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source)
                logging.info("Listening for voice input...")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            text = self.recognizer.recognize_google(audio, language=self.language)
            logging.info("Voice input transcribed successfully.")
            return text
        except sr.WaitTimeoutError:
            logging.warning("No speech detected within the timeout period.")
            return "No speech detected."
        except sr.UnknownValueError:
            logging.error("Google Speech Recognition could not understand audio.")
            return "Speech could not be understood."
        except sr.RequestError as e:
            logging.error(f"Could not request results from Google Speech Recognition service; {e}")
            return "Speech Recognition service error."
        except Exception as e:
            logging.error(f"An unexpected error occurred during voice capture: {e}")
            return "An unexpected error occurred."
