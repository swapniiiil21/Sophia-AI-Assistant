# command.py
import time
import speech_recognition as sr
import eel
import datetime
import wikipedia
import pyjokes
import requests
import spacy
import re
import os 

from engine.google_calendar import get_upcoming_events
from engine.speak import speak, chatgpt_response 
# The imports from features.py are now correctly linked to the db module via features.py itself
from engine.features import add_contact, get_contact_number, list_contacts, send_whatsapp_message 

# Load spaCy English model once
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("SpaCy 'en_core_web_sm' model not found. Downloading...")
    speak("Downloading necessary language model. Please wait a moment.")
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")
    speak("Language model downloaded. I'm ready.")


# Exposed function to handle speech commands from JavaScript (This is where takeCommand is called)
@eel.expose
def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print('Listening...')
        eel.DisplaySophiaMessage('Listening...')() 
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source)
        try:
            audio = r.listen(source, timeout=10, phrase_time_limit=6)
        except Exception:
            print("No audio detected.")
            return ""

    try:
        print('Recognizing...')
        eel.DisplaySophiaMessage('Recognizing...')()
        query = r.recognize_google(audio, language='en')
        print(f'User said: {query}')
        time.sleep(1) 
        eel.DisplaySophiaMessage(f"You said: {query}")() 
    except Exception as e:
        print(f"Speech recognition error: {e}. Say that again please...")
        eel.DisplaySophiaMessage("Sorry, I didn't catch that. Please say it again.")()
        return "" 

    return query.lower()


# Exposed function to make Sophia speak a greeting (called from main.js after face recognition)
@eel.expose
def speakSophiaGreeting(message):
    """
    Receives a greeting message from JavaScript and makes Sophia speak it aloud.
    """
    print(f"Sophia speaking greeting: {message}")
    speak(message) # Call the speak function from engine.speak

# Exposed function to handle all commands (from mic button)
@eel.expose
def allCommands():
    eel.DisplaySophiaMessage("Listening...")() 
    speak("Listening...") 

    query = takeCommand() 

    if not query:
        print("No command detected.")
        eel.ShowHood()() 
        return

    print(f"Command received: {query}")

    try:
        if 'open' in query:
            from engine.features import openCommand
            openCommand(query)

        elif 'play' in query and 'youtube' in query:
            from engine.features import PlayYoutube
            PlayYoutube(query)

        elif 'time' in query:
            now = datetime.datetime.now().strftime("%I:%M %p")
            response = f"The current time is {now}"
            speak(response)
            eel.DisplaySophiaMessage(response)() 

        elif 'date' in query:
            today = datetime.datetime.now().strftime("%B %d, %Y")
            response = f"Today's date is {today}"
            speak(response)
            eel.DisplaySophiaMessage(response)() 

        elif 'wikipedia' in query:
            wikipedia_term = query.replace("wikipedia", "").strip()
            if not wikipedia_term:
                response = "Please tell me what you want to search on Wikipedia."
                speak(response)
                eel.DisplaySophiaMessage(response)()
            else:
                speak(f"Searching Wikipedia for {wikipedia_term}...")
                eel.DisplaySophiaMessage(f"Searching Wikipedia for {wikipedia_term}...")()
                try:
                    summary = wikipedia.summary(wikipedia_term, sentences=2)
                    response = summary
                    speak(response)
                    eel.DisplaySophiaMessage(response)()
                except wikipedia.exceptions.PageError:
                    response = f"Sorry, I couldn't find a Wikipedia page for '{wikipedia_term}'."
                    speak(response)
                    eel.DisplaySophiaMessage(response)()
                except wikipedia.exceptions.DisambiguationError as e:
                    response = f"Your Wikipedia query '{wikipedia_term}' is ambiguous. Please be more specific. Possible options include: {', '.join(e.options[:3])}."
                    speak(response)
                    eel.DisplaySophiaMessage(response)()
                except Exception as e:
                    response = f"Sorry, something went wrong while searching Wikipedia: {str(e)}"
                    speak(response)
                    eel.DisplaySophiaMessage(response)()

        elif 'joke' in query:
            joke = pyjokes.get_joke()
            speak(joke)
            eel.DisplaySophiaMessage(joke)() 

        elif 'weather' in query or 'temperature' in query:
            city = extract_city_name(query)
            if city:
                get_weather(city) # get_weather function handles its own speak and DisplaySophiaMessage
            else:
                speak("Please tell me the city name.")
                eel.DisplaySophiaMessage("Please tell me the city name.")()
                city = takeCommand() 
                if city:
                    get_weather(city)
                else:
                    response = "Sorry, I didn't get the city name."
                    speak(response)
                    eel.DisplaySophiaMessage(response)()

        elif 'calculate' in query:
            speak("What calculation should I perform?")
            eel.DisplaySophiaMessage("What calculation should I perform?")()
            expression = takeCommand() 
            if not expression:
                response = "No calculation expression provided."
                speak(response)
                eel.DisplaySophiaMessage(response)()
                return
            try:
                # Basic and unsafe eval - for simple calculator use.
                # In a production app, use safer parsing (e.g., math.eval from sympy or custom parser)
                result = eval(expression)
                response = f"The result is {result}"
                speak(response)
                eel.DisplaySophiaMessage(response)()
            except Exception as e:
                response = f"Sorry, I couldn't calculate that. Please provide a valid mathematical expression. Error: {str(e)}"
                speak(response)
                eel.DisplaySophiaMessage(response)()

        elif 'event' in query or 'calendar' in query:
            speak("Checking your upcoming events.")
            eel.DisplaySophiaMessage("Checking your upcoming events.")()
            events = get_upcoming_events()
            if not events:
                response = "You have no upcoming events."
                speak(response)
                eel.DisplaySophiaMessage(response)()
            else:
                response = f"You have {len(events)} upcoming events."
                speak(response)
                eel.DisplaySophiaMessage(response)()
                for event in events:
                    start = event['start'].get('dateTime', event['start'].get('date'))
                    summary = event.get('summary', 'No Title')
                    try:
                        dt = datetime.datetime.fromisoformat(start.replace('Z', '+00:00'))
                        start_str = dt.strftime("%B %d, %I:%M %p")
                    except Exception:
                        start_str = start
                    event_response = f"On {start_str}, {summary}."
                    speak(event_response)
                    eel.DisplaySophiaMessage(event_response)() 
        
        # --- NEW WHATSAPP & CONTACT COMMANDS ---
        elif 'add contact' in query:
            speak("What name should I save this contact as?")
            eel.DisplaySophiaMessage("What name should I save this contact as?")()
            contact_name = takeCommand().strip()
            if not contact_name:
                speak("No name provided. Contact not added.")
                eel.DisplaySophiaMessage("No name provided. Contact not added.")()
                return
            
            speak(f"What is the 10-digit phone number for {contact_name}?")
            eel.DisplaySophiaMessage(f"What is the 10-digit phone number for {contact_name}?")()
            number_raw = takeCommand().strip()
            phone_number = "".join(filter(str.isdigit, number_raw))

            if not phone_number or len(phone_number) != 10:
                speak("Invalid phone number. Contact not added.")
                eel.DisplaySophiaMessage("Invalid phone number. Contact not added.")()
                return
            
            add_contact(contact_name, phone_number) # Call the function from features.py

        elif 'show my contacts' in query or 'list my contacts' in query:
            contacts = list_contacts()
            if not contacts:
                speak("You have no contacts saved.")
                eel.DisplaySophiaMessage("You have no contacts saved.")()
            else:
                speak("Here are your saved contacts:")
                eel.DisplaySophiaMessage("Here are your saved contacts:")()
                for name, number in contacts:
                    speak(f"{name}: {number}")
                    eel.DisplaySophiaMessage(f"{name}: {number}")()

        elif 'whatsapp message to' in query:
            # Extract contact name and message from the query
            parts = query.split('whatsapp message to', 1) # Split only on the first occurrence
            if len(parts) < 2:
                speak("Please specify the contact name and your message.")
                eel.DisplaySophiaMessage("Please specify the contact name and your message.")()
                return
            
            remaining_query = parts[1].strip()
            # Try to find a clear separation like "message is" or "saying"
            msg_keywords = ["message is", "saying", "that says"]
            message_start_index = -1
            for keyword in msg_keywords:
                if keyword in remaining_query:
                    message_start_index = remaining_query.find(keyword)
                    break
            
            if message_start_index != -1:
                contact_name = remaining_query[:message_start_index].strip()
                message_content = remaining_query[message_start_index + len(keyword):].strip()
            else:
                # Fallback if no clear keyword, assume everything after name is message
                # This is a bit tricky for voice, might need further refinement
                speak("Please be more specific about the message after the contact name. What is the message?")
                eel.DisplaySophiaMessage("Please be more specific about the message after the contact name. What is the message?")()
                message_content = takeCommand().strip()
                contact_name = remaining_query # Use what was left as name, user will re-speak message
                if not message_content:
                    speak("No message provided. Aborting WhatsApp message.")
                    eel.DisplaySophiaMessage("No message provided. Aborting WhatsApp message.")()
                    return

            if not contact_name:
                speak("I didn't get the contact name. Please try again.")
                eel.DisplaySophiaMessage("I didn't get the contact name. Please try again.")()
                return

            speak(f"Sending WhatsApp message to {contact_name} saying: {message_content}")
            eel.DisplaySophiaMessage(f"Sending WhatsApp message to {contact_name} saying: {message_content}")()
            send_whatsapp_message(contact_name, message_content, by_name=True) # Call with by_name=True


        elif 'whatsapp' in query: # Original handler for WhatsApp by number (kept as fallback)
            speak("To whom should I send the WhatsApp message? Please say the 10 digit number.")
            eel.DisplaySophiaMessage("To whom should I send the WhatsApp message? Please say the 10 digit number.")()
            number_raw = takeCommand()
            
            phone_number = "".join(filter(str.isdigit, number_raw))
            
            if not phone_number or len(phone_number) != 10:
                response = "I couldn't understand the phone number. Please try again with a valid 10-digit number."
                speak(response)
                eel.DisplaySophiaMessage(response)()
                return

            speak("What message would you like to send?")
            eel.DisplaySophiaMessage("What message would you like to send?")()
            message = takeCommand()

            if not message:
                response = "No message provided. Aborting WhatsApp message."
                speak(response)
                eel.DisplaySophiaMessage(response)()
                return
            
            speak(f"Sending WhatsApp message to {phone_number} with message: {message}")
            eel.DisplaySophiaMessage(f"Sending WhatsApp message to {phone_number} with message: {message}")()
            
            send_whatsapp_message(phone_number, message, by_name=False) # Call with by_name=False


        else:
            # Fallback to Gemini (now handled by chatgpt_response which is Gemini-based)
            speak("Let me think about that...")
            eel.DisplaySophiaMessage("Let me think about that...")() 
            answer = chatgpt_response(query)
            if answer:
                speak(answer)
                eel.DisplaySophiaMessage(answer)() 
            else:
                response = "Sorry, I couldn't get a response from the AI backend at this time."
                speak(response)
                eel.DisplaySophiaMessage(response)() 

    except Exception as e:
        error_message = f"Oops! An unexpected error occurred while processing your command: {str(e)}"
        speak(error_message)
        eel.DisplaySophiaMessage(error_message)() 

    eel.ShowHood()() 


def extract_city_name(text):
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "GPE": 
            return ent.text

    patterns = [
        r'weather in ([a-zA-Z\s]+)',
        r'temperature in ([a-zA-Z\s]+)',
        r'in ([a-zA-Z\s]+) weather',
        r'in ([a-zA-Z\s]+) temperature',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()

    return None


def get_weather(city):
    api_key = "75770f09e08718e80aa7576528a9a3b1"  # Your OpenWeatherMap API key
    base_url = "http://api.openweathermap.org/data/2.5/weather"

    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"
    }

    try:
        response = requests.get(base_url, params=params, timeout=5)
        data = response.json()

        if response.status_code != 200 or str(data.get("cod")) != "200":
            message = data.get("message", "Unknown error occurred.")
            speak(f"Sorry, I couldn't find weather data for {city}. {message.capitalize()}.")
            eel.DisplaySophiaMessage(f"Sorry, I couldn't find weather data for {city}. {message.capitalize()}.")() 
            return

        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]
        country = data["sys"].get("country", "")
        city_name = data.get("name", city).title()

        final_message = f"The temperature in {city_name}, {country} is {temp} degrees Celsius with {desc}."
        speak(final_message)
        eel.DisplaySophiaMessage(final_message)() 

    except requests.exceptions.RequestException:
        speak("Sorry, I couldn't get the weather information due to a network issue.")
        eel.DisplaySophiaMessage("Sorry, I couldn't get the weather information due to a network issue.")() 

    except Exception as e:
        speak(f"An unexpected error occurred while fetching weather details: {str(e)}")
        eel.DisplaySophiaMessage(f"An unexpected error occurred while fetching weather details: {str(e)}")() 

# This function receives messages from the JavaScript frontend's chatbox.
@eel.expose
def sendUserMessage(message, thinking_message_id=None):
    print(f"Python received user message from chatbox: {message} with thinking ID: {thinking_message_id}")
    
    response_text = chatgpt_response(message) 
    
    if response_text:
        speak(response_text) 
        # Pass the thinking_message_id back to JavaScript to update the placeholder
        eel.DisplaySophiaMessage(response_text, thinking_message_id)() 
    else:
        fallback_message = "Sorry, I couldn't process that text command or get a response from the AI."
        speak(fallback_message)
        eel.DisplaySophiaMessage(fallback_message, thinking_message_id)() 
