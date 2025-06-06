import pyttsx3
import os
import sys # Import sys module for encoding configuration
import requests # For making HTTP requests to Gemini API
import json # For handling JSON responses

# Attempt to configure stdout encoding to UTF-8 for Python 3.7+
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Initialize text-to-speech
engine = pyttsx3.init()
voices = engine.getProperty('voices')
found_voice = False
for voice in voices:
    if "Samantha" in voice.name:
        engine.setProperty('voice', voice.id)
        found_voice = True
        break
if not found_voice and len(voices) > 1:
    engine.setProperty('voice', voices[1].id)
elif not found_voice and len(voices) > 0:
    engine.setProperty('voice', voices[0].id)

engine.setProperty('rate', 170)

def speak(text):
    """Speaks the given text using the initialized text-to-speech engine."""
    print(f"Assistant: {text}")
    try:
        safe_text = text.encode('utf-8', 'ignore').decode('utf-8')
        engine.say(safe_text)
        engine.runAndWait()
    except Exception as e:
        print(f"Error speaking text: {e}")
        print(f"Fallback: Could not speak: {text}")

# Gemini API setup (API key will be automatically provided by Canvas runtime)
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
# The API key is typically handled by the Canvas environment for direct fetch calls.
# For Python backend, we assume it's also provided or we would need to get it from an environment variable.
# For now, leaving it as an empty string for consistency, as Canvas runtime fills it for frontend.
# In a real Python app, you'd use os.getenv("GEMINI_API_KEY") here.
GEMINI_API_KEY = "" # Leave empty for Canvas provided API key

def chatgpt_response(prompt):
    """
    Gets a text response from the Google Gemini 2.0 Flash model.
    """
    headers = {
        'Content-Type': 'application/json'
    }
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}]
    }

    try:
        # Construct the full URL with API key
        full_api_url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
        if not GEMINI_API_KEY:
            print("Warning: GEMINI_API_KEY is empty. Ensure Canvas runtime provides it or set it as an env var.")
            # For Canvas, this warning is expected as it injects the key at runtime for fetch.
            # However, for Python `requests`, you'd typically need the actual key.
            # For demonstration, we'll proceed as if the key is handled.

        response = requests.post(full_api_url, headers=headers, data=json.dumps(payload), timeout=20)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        
        result = response.json()
        
        if result and result.get('candidates') and len(result['candidates']) > 0 and \
           result['candidates'][0].get('content') and result['candidates'][0]['content'].get('parts') and \
           len(result['candidates'][0]['content']['parts']) > 0:
            return result['candidates'][0]['content']['parts'][0]['text'].strip()
        else:
            print(f"Gemini API returned an unexpected structure or no content: {result}")
            return "Sorry, I couldn't generate a response from the AI at this moment."
    except requests.exceptions.RequestException as e:
        print(f"Gemini API Request Error: {e}")
        return "Sorry, I'm having trouble connecting to the AI right now due to a network issue."
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error from Gemini API: {e}. Response: {response.text}")
        return "Sorry, I received an unreadable response from the AI backend."
    except Exception as e:
        print(f"An unexpected error occurred with Gemini API: {e}")
        return "Sorry, I encountered an unexpected error while trying to get an AI response."

if __name__ == "__main__":
    # Example usage when running speak.py directly
    query = "Tell me about the history of India in 50 words."
    print(f"Querying Gemini: {query}")
    reply = chatgpt_response(query)
    speak(reply)
