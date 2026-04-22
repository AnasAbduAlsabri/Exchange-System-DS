import sys
import os

# Add the Exchange_System directory to the path so we can import the app
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Exchange_System'))

from app import app

# Vercel needs the application object to be named 'app'
# We don't use socketio.run() here because Vercel handles the server
application = app
