# This file can be left empty or used to import and expose route blueprints
from .main import main_bp
from .auth import auth_bp
from .admin import admin_bp

__all__ = ['main_bp', 'auth_bp', 'admin_bp']