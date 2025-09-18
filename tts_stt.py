# tts_stt.py
import speech_recognition as sr
import config # Import config to access the global engine and recognizer

def speak(text):
    """Converts text to speech using the initialized engine from config."""
    engine = config.get_engine()
    if engine:
        engine.say(text)
        engine.runAndWait()
    else:
        print("Text-to-speech engine not initialized in config.")

def recognize_speech(audio_data):
    """
    Recognizes speech from audio data using the recognizer from config.
    Returns the recognized text or an empty string if not understood.
    """
    recognizer = config.get_recognizer()
    if recognizer:
        try:
            return recognizer.recognize_google(audio_data).lower()
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
            return ""
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            return ""
        except Exception as e:
            print(f"An unexpected error occurred during speech recognition: {e}")
            return ""
    else:
        print("Speech recognizer not initialized in config.")
        return ""