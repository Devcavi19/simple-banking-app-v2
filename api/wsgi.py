import sys
import os

# Add the parent directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Initialize application variable
app = None

try:
    from app import app as flask_app
    
    # Set the app variable that Vercel expects
    app = flask_app
    
except Exception as e:
    print(f"Error importing app: {e}")
    import traceback
    traceback.print_exc()
    
    # Create a minimal Flask app if import fails
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def error():
        return f"Application failed to start: {str(e)}", 500
    
    @app.route('/<path:path>')
    def catch_all(path):
        return f"Application failed to start: {str(e)}", 500

# Ensure we always have an application
if app is None:
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def fallback():
        return "Application not initialized", 500

# For backwards compatibility
application = app