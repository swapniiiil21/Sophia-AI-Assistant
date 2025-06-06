import pyttsx3
engine = pyttsx3.init()
voices = engine.getProperty('voices')

for i, voice in enumerate(voices):
    print(f"Voice {i}:")
    print(f" - ID: {voice.id}")
    print(f" - Name: {voice.name}")
    print(f" - Languages: {voice.languages}")
    print()

