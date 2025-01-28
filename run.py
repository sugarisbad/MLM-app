import os
from app import create_app
from app.models import db

# Create the Flask application
app = create_app()

if __name__ == '__main__':
    # Ensure the app runs in debug mode for development
    app.run(debug=True, host='0.0.0.0', port=5000)