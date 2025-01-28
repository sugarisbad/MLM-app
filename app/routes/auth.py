from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app import db
from app.models import User
from app.utils.helpers import validate_username, validate_password
from app.utils.decorators import login_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # Redirect based on user role
        if current_user.is_admin:
            return redirect(url_for('main.dashboard'))
        else:
            return redirect(url_for('main.user_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            
            # Redirect based on user role after successful login
            if user.is_admin:
                return redirect(url_for('main.dashboard'))
            else:
                return redirect(url_for('main.user_dashboard'))
        
        flash('Invalid username or password', 'danger')
    
    return render_template('auth/login.html')  # Render the login template from the auth subdirectory

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    User registration route.
    
    Returns:
        Rendered registration template or redirects after successful registration
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        referrer_id = request.form.get('referrer_id')
        
        # Validate input
        if not validate_username(username):
            flash('Invalid username. Must be 3-20 characters, alphanumeric.', 'danger')
            return redirect(url_for('auth.register'))
        
        if not validate_password(password):
            flash('Invalid password. Must be at least 8 characters with uppercase, lowercase, and number.', 'danger')
            return redirect(url_for('auth.register'))
        
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return redirect(url_for('auth.register'))
        
        # Create new user
        new_user = User(username=username)
        new_user.set_password(password)
        
        # Handle referral if provided
        if referrer_id:
            try:
                referrer = User.query.get(int(referrer_id))
                if referrer:
                    new_user.referrer_id = referrer.id
            except ValueError:
                flash('Invalid referrer ID.', 'danger')
                return redirect(url_for('auth.register'))
        
        db.session.add(new_user)
        db.session.commit()
        
        # Log in the new user
        login_user(new_user)
        
        flash('Registration successful!', 'success')
        
        # Redirect based on user role
        if new_user.is_admin:
            return redirect(url_for('main.dashboard'))
        else:
            return redirect(url_for('main.user_dashboard'))
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return render_template('auth/logout.html')

# Add more authentication-related routes here