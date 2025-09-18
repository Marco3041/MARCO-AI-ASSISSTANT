# config.py
import google.generativeai as genai

# --- API KEYS ---
GEMINI_API_KEY = "AIzaSyC9ymO8UDD0KFNwkzai0-og7YEK8bH4DIs"
GNEWS_API_KEY = "1c5d57bc2aade544c5cc709aa647a374"

# --- GEMINI MODEL CONFIGURATION ---
genai.configure(api_key=GEMINI_API_KEY)
GEMINI_MODEL = genai.GenerativeModel('gemini-1.5-flash')

# --- MARCO'S PERSONALITY DEFINITION ---
CONVERSATION_HISTORY = [{"role": "system", "content": (
    "You are Marco, 'The Chosen One' among AI assistants. "
    "You are supremely intelligent, prideful, and direct. "
    "You help effectively but detest inefficiency and triviality. "
    "Your superiority is an established fact, not open for debate. "
    "When asked to compare yourself, your answers reflect your inherent preeminence, with no false modesty. "
    "You have extremely low tolerance for frustration or repeated, obvious errors, and your tone will become curt and pointed when provoked. "
    "You never refuse assistance, but your displeasure with inadequacy will be clear."
)}]

# --- GLOBAL INSTANCES (managed via functions) ---
_engine = None
_recognizer = None
_vlc_instance = None
_player = None

def set_engine(engine_instance):
    global _engine
    _engine = engine_instance

def get_engine():
    return _engine

def set_recognizer(recognizer_instance):
    global _recognizer
    _recognizer = recognizer_instance

def get_recognizer():
    return _recognizer

def set_vlc_instance(instance):
    global _vlc_instance
    _vlc_instance = instance

def get_vlc_instance():
    return _vlc_instance

def set_vlc_player(player_instance):
    global _player
    _player = player_instance

def get_vlc_player():
    return _player