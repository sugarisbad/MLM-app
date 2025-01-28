from functools import wraps
from flask import session, redirect, url_for, flash, abort, request
from flask_login import current_user

def login_required(f):
    """
    Decorator to require login for a route.
    
    Args:
        f (function): The route function to decorate
    
    Returns:
        function: Wrapped route function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """
    Decorator to require admin privileges for a route.
    
    Args:
        f (function): The route function to decorate
    
    Returns:
        function: Wrapped route function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You do not have permission to access this page.', 'danger')
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function

def referral_access_required(f):
    """
    Decorator to check referral access permissions.
    
    Args:
        f (function): The route function to decorate
    
    Returns:
        function: Wrapped route function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Add custom logic for referral access
        # For example, check if user has active referral status
        if not current_user.is_authenticated:
            flash('Please log in to access referral features.', 'warning')
            return redirect(url_for('auth.login'))
        
        # Add additional checks as needed
        return f(*args, **kwargs)
    return decorated_function