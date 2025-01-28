from flask import Flask, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_babel import Babel
from flask_talisman import Talisman
from flask_session import Session
from config.config import get_config
from datetime import date
from .utils.helpers import current_year  # Use relative import

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
babel = Babel()
talisman = Talisman()
session_manager = Session()

def create_app(config_name='development'):
    """
    Application factory function.
    
    Args:
        config_name (str): Configuration environment name
    
    Returns:
        Flask: Configured Flask application
    """
    # Get the appropriate configuration
    config = get_config()
    
    # Create Flask app instance
    app = Flask(__name__, 
                template_folder='../templates', 
                static_folder='../static')  # Explicitly set static folder
    app.config.from_object(config)
    
    # Explicitly set the secret key BEFORE initializing extensions
    app.config['SECRET_KEY'] = config.SECRET_KEY
    app.secret_key = config.SECRET_KEY  # Use config.SECRET_KEY directly
    
    # Configure session
    app.config['SESSION_TYPE'] = 'filesystem'  # or 'redis' if you prefer
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True  # Add this to sign the session cookie
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    babel.init_app(app)
    talisman.init_app(app, force_https=False)  # Disable force HTTPS
    session_manager.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        from .models import User
        return User.query.get(int(user_id))
    
    # Add current_user to template context
    @app.context_processor
    def inject_current_user():
        from flask_login import current_user
        return dict(current_user=current_user)
    
    # Configure Babel for internationalization
    @babel.localeselector
    def get_locale():
        return session.get('language', 'ru')
    
    # Add current_year to template context
    app.context_processor(lambda: {'current_year': current_year})
    
    # Register blueprints
    from .routes.main import main_bp
    from .routes.auth import auth_bp
    from .routes.admin import admin_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    
    # Configure logging
    import logging
    from logging.handlers import RotatingFileHandler
    
    # Create a file handler
    handler = RotatingFileHandler(
        'app.log',
        maxBytes=1024 * 1024 * 100,  # 100 MB
        backupCount=10
    )
    handler.setLevel(logging.INFO)
    
    # Create a logging format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    # Add the handler to the app's logger
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
    
    return app

# Import models to ensure they are recognized by Flask-SQLAlchemy
from . import models