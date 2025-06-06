import os
import sys
import subprocess
import webbrowser
import sqlite3
import datetime 
from playsound import playsound
import eel
import re
import pywhatkit as kit

from .speak import speak, chatgpt_response
from . import db # Corrected import: from . import db instead of database

# Connect to your local SQLite DB using the db module
# Note: For functions that perform multiple operations or need to keep connection open,
# you might pass conn/cursor explicitly or manage it differently.
# For simplicity here, we'll open/close connection per new database operation.

# --- New functions for Contacts (using db.py's connect_db) ---
def add_contact(name, phone_number):
    conn, cursor = db.connect_db() # Corrected call: db.connect_db
    try:
        cursor.execute('INSERT INTO contacts (name, phone_number) VALUES (?, ?)', (name.lower(), phone_number))
        conn.commit()
        speak(f"Contact {name} with number {phone_number} added successfully.")
        eel.DisplaySophiaMessage(f"Contact {name} with number {phone_number} added successfully.")()
        return True
    except sqlite3.IntegrityError:
        speak(f"Contact {name} already exists with number {phone_number}.")
        eel.DisplaySophiaMessage(f"Contact {name} already exists with number {phone_number}.")()
        return False
    except Exception as e:
        speak(f"Failed to add contact {name}: {e}")
        eel.DisplaySophiaMessage(f"Failed to add contact {name}: {e}")()
        return False
    finally:
        conn.close()

def get_contact_number(name):
    conn, cursor = db.connect_db() # Corrected call: db.connect_db
    try:
        cursor.execute('SELECT phone_number FROM contacts WHERE LOWER(name) = ?', (name.lower(),))
        result = cursor.fetchone()
        if result:
            return result[0]
        return None
    finally:
        conn.close()

def list_contacts():
    conn, cursor = db.connect_db() # Corrected call: db.connect_db
    try:
        cursor.execute('SELECT name, phone_number FROM contacts')
        results = cursor.fetchall()
        return results
    finally:
        conn.close()

# Original functions (ensure they use the speak and eel functions properly)
def playAssistantSound():
    music_dir = os.path.join("www", "assets", "audio", "start_sound.mp3")
    playsound(music_dir)

@eel.expose
def playClickSound():
    music_dir = os.path.join("www", "assets", "audio", "click_sound.mp3")
    playsound(music_dir)

def openCommand(query):
    query = query.lower().replace("open", "").strip() 

    if not query:
        speak("Please tell me what to open.")
        return

    conn, cursor = db.connect_db() # Corrected call: db.connect_db # Get a fresh connection for this operation
    try:
        # Try to open app from database path
        cursor.execute('SELECT path FROM sys_command WHERE LOWER(name) = ?', (query,))
        results = cursor.fetchall()

        if results:
            speak(f"Opening {query}")
            path = results[0][0]

            if sys.platform == 'darwin':  # macOS
                subprocess.call(["open", path])
            elif os.name == 'nt':  # Windows
                os.startfile(path)
            elif os.name == 'posix':  # Linux
                subprocess.call(["xdg-open", path])
            else:
                speak("Sorry, I can't open applications on this operating system.")
            return

        # Try to open web URL from database
        cursor.execute('SELECT url FROM web_command WHERE LOWER(name) = ?', (query,))
        results = cursor.fetchall()

        if results:
            speak(f"Opening {query}")
            webbrowser.open(results[0][0])
            return

        # Fallback: try to open query as URL or app name
        speak(f"Trying to open {query}")
        if sys.platform == 'darwin':
            subprocess.call(["open", query])
        elif os.name == 'nt':
            os.system(f"start {query}")
        elif os.name == 'posix':
            subprocess.call(["xdg-open", query])
        else:
            speak(f"Unable to open {query} on this OS.")

    except Exception as e:
        speak(f"Sorry, something went wrong while trying to open {query}. {str(e)}")
    finally:
        conn.close() # Close connection after operation


def extract_yt_term(command):
    pattern = r'play\s+(.*?)\s+on\s+youtube'
    match = re.search(pattern, command, re.IGNORECASE)
    return match.group(1) if match else None

def PlayYoutube(query):
    search_term = extract_yt_term(query)
    if search_term:
        speak(f"Playing {search_term} on YouTube")
        kit.playonyt(search_term)
    else:
        speak("Sorry, I couldn't understand what to play on YouTube.")

def send_whatsapp_message(recipient_info, message, by_name=False):
    phone_number = None
    if by_name:
        phone_number = get_contact_number(recipient_info) # Use the new get_contact_number function
        if not phone_number:
            speak(f"Sorry, I could not find a contact named {recipient_info} in your contacts.")
            eel.DisplaySophiaMessage(f"Sorry, I could not find a contact named {recipient_info} in your contacts.")()
            return
    else: # It's a raw number
        phone_number = recipient_info

    try:
        now = datetime.datetime.now()
        # Schedule message 2 minutes from now to give time for WhatsApp Web to open
        future_minute = now.minute + 2
        future_hour = now.hour
        
        # Handle minute rollover to next hour
        if future_minute >= 60:
            future_minute -= 60
            future_hour = (future_hour + 1) % 24 # Handle hour rollover (0-23)

        # pywhatkit expects phone number with country code, e.g., +91 for India
        # Assuming the user provides a 10-digit number for India, we prefix +91
        full_phone_number = f"+91{phone_number}"

        speak(f"Scheduling WhatsApp message to {recipient_info} at {future_hour:02d}:{future_minute:02d}.")
        eel.DisplaySophiaMessage(f"Scheduling WhatsApp message to {recipient_info} at {future_hour:02d}:{future_minute:02d}.")()
        
        kit.sendwhatmsg(full_phone_number, message, future_hour, future_minute, wait_time=40, tab_close=False) # Increased wait_time, kept tab open
        
        speak("WhatsApp message initiated. Please check your browser to confirm delivery.")
        eel.DisplaySophiaMessage("WhatsApp message initiated. Please check your browser to confirm delivery.")()
    except Exception as e:
        speak(f"Failed to send WhatsApp message: {e}")
        eel.DisplaySophiaMessage(f"Failed to send WhatsApp message: {e}")()
