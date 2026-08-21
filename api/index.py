import os
import sys
import traceback

# Ensure root directory is in sys.path
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

try:
    from app import app
    handler = app
except Exception as e:
    from flask import Flask, Response
    app = Flask(__name__)
    err_msg = traceback.format_exc()
    print(f"[Vercel Handler Error]: {err_msg}")
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        return Response(f"<h3>Application Initialization Warning</h3><pre>{err_msg}</pre>", status=500, mimetype='text/html')
    handler = app
