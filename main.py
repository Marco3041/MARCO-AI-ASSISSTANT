# main.py
import tkinter as tk
import speech_recognition as sr
import pyttsx3
import sys

# Import custom modules
import config
from media_player import init_vlc # Only need this for initial setup
from gui_interface import MarcoGUI # Import your new GUI class

def main():
    # --- GLOBAL INITIALIZATIONS ---
    # Initialize pyttsx3 engine and store its instance in config
    # This must be done on the main thread
    engine = pyttsx3.init()
    config.set_engine(engine)

    # Initialize SpeechRecognizer and store its instance in config
    r = sr.Recognizer()
    config.set_recognizer(r)

    # Initialize VLC player and store its instances in config
    # This must also be done on the main thread (or its own dedicated thread if Vlc is problematic)
    init_vlc()

    # --- GUI Setup ---
    root = tk.Tk()
    app = MarcoGUI(root)

    # --- Start Tkinter event loop ---
    root.mainloop()

    # Clean up VLC player resources when the GUI window is closed
    player = config.get_vlc_player()
    if player and player.is_playing():
        player.stop()
    # You might also want to release the vlc instance if necessary
    # config.get_vlc_instance().release() # Uncomment if you need explicit release

    print("Marco AI Assistant application closed.")


if __name__ == "__main__":
    main()