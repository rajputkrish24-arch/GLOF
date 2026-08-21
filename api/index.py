import os
import sys

# Ensure parent directory is in sys.path so app modules are discoverable
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from app import app

# Expose WSGI application object for Vercel serverless functions
app = app
