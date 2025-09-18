# media_player.py
import vlc
import yt_dlp
from tts_stt import speak # For speaking feedback
import config # For global VLC instance/player access

def init_vlc():
    """Initializes the global VLC instance and player and stores them in config."""
    vlc_instance = vlc.Instance()
    player = vlc_instance.media_player_new()
    config.set_vlc_instance(vlc_instance)
    config.set_vlc_player(player)

def get_vlc_player():
    """Returns the globally initialized VLC player instance from config."""
    return config.get_vlc_player()

def play_youtube_audio(song_query):
    """
    Searches for and plays audio from YouTube using yt_dlp and VLC.
    """
    player = config.get_vlc_player()
    if not player:
        speak("VLC player not initialized. Cannot play music.")
        return

    if not song_query:
        speak("Please specify the audio required for playback.")
        return

    speak(f"Searching for {song_query} on YouTube.")
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'extract_flat': False,
            'force_generic_extractor': True,
            'default_search': 'ytsearch',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(f"{song_query}", download=False)

            if 'entries' in info_dict and info_dict['entries']:
                video_info = info_dict['entries'][0]
                stream_url = video_info.get('url')

                if stream_url:
                    if player.is_playing():
                        player.stop()

                    media = config.get_vlc_instance().media_new(stream_url)
                    player.set_media(media)
                    player.play()
                    speak(f"Playing {video_info.get('title', song_query)}.")
                else:
                    speak(f"Could not find a direct streamable link for {song_query}. The video might be geo-restricted or unavailable for direct streaming.")
            else:
                speak(f"Sorry, I could not find any song matching {song_query} on YouTube or the search yielded no valid results.")

    except Exception as e:
        speak(f"An error occurred during music playback. Kindly verify your internet connection or select an alternative track.")
        print(f"Music playback error: {e}")

def stop_vlc_player():
    """Stops the currently playing audio."""
    player = config.get_vlc_player()
    if player and player.is_playing():
        player.stop()
        speak("Music playback terminated.")
    else:
        speak("No audio is currently active.")