# news_api.py
import requests
import config # To access GNEWS_API_KEY
from tts_stt import speak # For speaking news headlines

def get_news(country=None, topic=None):
    """
    Fetches and reads top news headlines based on country or topic using the GNews API.
    """
    api_url = ""
    if country:
        speak(f"Fetching top headlines from {country.upper()}.")
        api_url = f"https://gnews.io/api/v4/top-headlines?lang=en&country={country}&token={config.GNEWS_API_KEY}"
    elif topic:
        speak(f"Fetching top {topic} headlines.")
        api_url = f"https://gnews.io/api/v4/top-headlines?lang=en&topic={topic}&token={config.GNEWS_API_KEY}"
    else:
        speak("Error: No country or topic specified for news.")
        return

    try:
        r = requests.get(api_url, timeout=30)
        r.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)

        data = r.json()
        articles = data.get('articles', [])

        if not articles:
            speak("No relevant news articles found at the moment.")
        else:
            speak("Presenting the top headlines.")
            for i, article in enumerate(articles[:5]): # Limiting to 5 articles for brevity
                news_title = article.get('title', 'No title available')
                print(f"{i+1}. {news_title}")
                speak(news_title)

    except requests.exceptions.RequestException as e:
        speak("Unable to access news feeds due to network issues or an API error. Verify internet connection or API key.")
        print(f"News API error: {e}")
    except Exception as e:
        speak("An unexpected anomaly occurred during news fetching.")
        print(f"General news error: {e}")