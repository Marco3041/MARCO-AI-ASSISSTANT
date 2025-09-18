# assistant_actions.py
import webbrowser
import sys # Still good to have for explicit exit handling, though GUI now orchestrates

# Import functions from other modules
from tts_stt import speak # Still needed for Marco's AI responses
from media_player import play_youtube_audio, stop_vlc_player, get_vlc_player
from news_api import get_news
from llm_interaction import get_gemini_response # This function already calls speak internally

def process_command(command):
    """
    Processes the given command (voice or text) and executes the corresponding action.
    Returns a status string or 'exit_program'.
    """
    command = command.lower()
    
    player = get_vlc_player()

    # --- Core Commands ---
    if "marco stop" in command:
        stop_vlc_player() # This function now handles its own speak()
        return "exit_program" # Signal to main.py (via GUI) to exit

    # --- Web Browser Commands ---
    elif "open google" in command:
        webbrowser.open("https://www.google.com")
        speak("Opening Google.") # Marco still announces
        return "Opened Google."
    elif "open facebook" in command:
        webbrowser.open("https://www.facebook.com")
        speak("Opening Facebook.")
        return "Opened Facebook."
    elif "open youtube" in command:
        webbrowser.open("https://www.youtube.com")
        speak("Opening YouTube.")
        return "Opened YouTube."
    elif "open linkedin" in command:
        webbrowser.open("https://www.linkedin.com")
        speak("Opening LinkedIn.")
        return "Opened LinkedIn."

    # --- Music Playback Commands ---
    elif command.startswith("play"):
        song_query = command.replace("play", "").strip()
        play_youtube_audio(song_query) # This function handles its own speak()
        return "Searching for and playing music."
    elif "stop music" in command or "stop song" in command:
        stop_vlc_player() # This function handles its own speak()
        return "Music control command processed."

    # --- News Commands ---
    elif "news" in command:
        if "indian news" in command or "india news" in command:
            get_news(country='in') # This function handles its own speak()
            return "Fetching Indian news."
        elif "international news" in command or "global news" in command:
            get_news(topic='breaking') # This function handles its own speak()
            return "Fetching international news."
        else:
            speak("Specify desired news. Options are: 'Indian news' or 'International news'.")
            return "Clarification needed for news."

    # --- Program Exit Commands ---
    elif "exit" in command or "quit" in command or "goodbye" in command:
        stop_vlc_player() # Ensure music stops before exit (this calls speak internally)
        return "exit_program" # Signal to main.py (via GUI) to exit

    # --- Fallback to LLM for unhandled commands ---
    else:
        # LLM interaction module handles its own speaking
        get_gemini_response(command)
        return "LLM processed your request." # Generic status for LLM interaction