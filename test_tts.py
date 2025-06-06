import pyttsx3

engine = pyttsx3.init()
voices = engine.getProperty('voices')
print("Available voices:")
for i, voice in enumerate(voices):
    print(f"{i}: {voice.name} - {voice.id}")

engine.setProperty('voice', voices[0].id)  # Change index if needed
engine.setProperty('rate', 170)
engine.say("Hello, this is a test from pyttsx3 on macOS.")
engine.runAndWait()

