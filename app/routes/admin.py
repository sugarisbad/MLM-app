from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user
from app import db
from app.models import User, Transaction, ReferralSettings
from app.utils.decorators import admin_required
from app.utils.helpers import validate_username, validate_password

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@admin_required
def dashboard():
    """
    Admin dashboard route.
    
    Returns:
        Rendered admin dashboard template
    """
    # Fetch key statistics
    total_users = User.query.count()
    total_transactions = Transaction.query.count()
    total_revenue = db.session.query(db.func.sum(Transaction.amount)).scalar() or 0
    
    context = {
        'total_users': total_users,
        'total_transactions': total_transactions,
        'total_revenue': total_revenue
    }
    
    return render_template('admin/dashboard.html', **context)

@admin_bp.route('/users')
@admin_required
def user_list():
    """
    List all users for admin review.
    
    Returns:
        Rendered user list template
    """
    users = User.query.all()
    return render_template('admin/user_list.html', users=users)

@admin_bp.route('/user/<int:user_id>')
@admin_required
def user_detail(user_id):
    """
    Detailed view of a specific user for admin.
    
    Args:
        user_id (int): ID of the user to view
    
    Returns:
        Rendered user detail template
    """
    user = User.query.get_or_404(user_id)
    transactions = Transaction.query.filter_by(user_id=user_id).order_by(Transaction.created_at.desc()).all()
    
    context = {
        'user': user,
        'transactions': transactions
    }
    
    return render_template('admin/user_detail.html', **context)

@admin_bp.route('/referral-settings', methods=['GET', 'POST'])
@admin_required
def referral_settings():
    """
    Manage referral settings.
    
    Returns:
        Rendered referral settings template or redirects after update
    """
    if request.method == 'POST':
        # Process referral settings update
        levels = request.form.getlist('level')
        percentages = request.form.getlist('percentage')
        
        # Clear existing settings and create new ones
        ReferralSettings.query.delete()
        
        for level, percentage in zip(levels, percentages):
            setting = ReferralSettings(
                level=int(level),
                percentage=float(percentage)
            )
            db.session.add(setting)
        
        db.session.commit()
        flash('Referral settings updated successfully!', 'success')
        return redirect(url_for('admin.referral_settings'))
    
    # Fetch current referral settings
    settings = ReferralSettings.query.order_by(ReferralSettings.level).all()
    return render_template('admin/referral_settings.html', settings=settings)

@admin_bp.route('/create-admin', methods=['GET', 'POST'])
@admin_required
def create_admin():
    """
    Create a new admin user.
    
    Returns:
        Rendered create admin template or redirects after creation
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Validate input
        if not validate_username(username):
            flash('Invalid username. Must be 3-20 characters, alphanumeric.', 'danger')
            return redirect(url_for('admin.create_admin'))
        
        if not validate_password(password):
            flash('Invalid password. Must be at least 8 characters with uppercase, lowercase, and number.', 'danger')
            return redirect(url_for('admin.create_admin'))
        
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return redirect(url_for('admin.create_admin'))
        
        # Create new admin user
        new_admin = User(username=username, is_admin=True)
        new_admin.set_password(password)
        
        db.session.add(new_admin)
        db.session.commit()
        
        flash('New admin user created successfully!', 'success')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/create_admin.html')