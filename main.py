import os
import sys
import eel
from engine.features import *
from engine.command import *

eel.init('www')

playAssistantSound()

# Open browser in macOS friendly way:
if sys.platform == 'darwin':  # macOS
    # open default browser to local eel server
    import webbrowser
    webbrowser.open('http://localhost:8000/index.html')
elif os.name == 'nt':  # Windows
    os.system('start chrome.exe --app="http://localhost:8000/index.html"')
else:
    # Linux fallback
    os.system('xdg-open http://localhost:8000/index.html')

# Start eel server on port 8000 or change port if needed
try:
    eel.start('index.html', mode=None, host='localhost', port=8000, block=True)
except OSError as e:
    if "Address already in use" in str(e):
        print("Port 8000 is busy, trying port 8001")
        eel.start('index.html', mode=None, host='localhost', port=8001, block=True)
    else:
        raise
