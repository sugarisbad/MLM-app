import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        import secrets
        SECRET_KEY = secrets.token_hex(32)
        print("WARNING: No SECRET_KEY set. Generated a temporary secret key. Set a permanent key in .env file.")
    
    # Validate secret key length
    if len(SECRET_KEY) < 32:
        raise ValueError("SECRET_KEY must be at least 32 characters long for security.")
    SQLALCHEMY_DATABASE_URI = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security settings
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    
    # Babel internationalization settings
    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_DEFAULT_TIMEZONE = 'UTC'
    LANGUAGES = ['en', 'ru']
    
    # Logging configuration
    LOG_TO_STDOUT = os.getenv('LOG_TO_STDOUT', 'false') == 'true'

class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = False
    SESSION_COOKIE_SAMESITE = None

class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    TESTING = True

class StagingConfig(Config):
    DEBUG = False

def get_config():
    """
    Get the appropriate configuration based on the environment.
    
    Returns:
        Config: Configuration class based on the current environment.
    """
    env = os.getenv('FLASK_ENV', 'development')
    config_map = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig,
        'staging': StagingConfig
    }
    return config_map.get(env, DevelopmentConfig)