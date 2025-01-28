from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from app.models import User, Transaction
from app.utils.decorators import login_required, admin_required
from app import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def landing():
    """
    Landing page route.
    
    Returns:
        Rendered landing page template
    """
    current_language = session.get('language', 'en')
    return render_template('landing.html', current_language=current_language)

@main_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """
    Admin dashboard route.
    
    Returns:
        Rendered dashboard template with admin statistics
    """
    from datetime import datetime, timedelta
    
    # Fetch recent transactions
    transactions = Transaction.query.order_by(Transaction.created_at.desc()).limit(5).all()
    
    # Calculate admin statistics
    stats = {
        'total_users': User.query.count(),
        'total_balance': User.query.with_entities(db.func.sum(User.balance)).scalar() or 0,
        'today_registrations': User.query.filter(
            User.created_at >= datetime.utcnow().date()
        ).count()
    }
    
    # Prepare dashboard context
    context = {
        'user': current_user,
        'recent_transactions': transactions,
        'stats': stats
    }
    
    return render_template('admin/dashboard.html', **context)

@main_bp.route('/user/dashboard')
@login_required
def user_dashboard():
    """
    User dashboard route for non-admin users.
    
    Returns:
        Rendered user dashboard template with user information
    """
    from datetime import datetime, timedelta
    
    # Fetch recent transactions for the current user
    transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.created_at.desc()).limit(5).all()
    
    # Calculate monthly balance change
    one_month_ago = datetime.utcnow() - timedelta(days=30)
    monthly_transactions = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        Transaction.created_at >= one_month_ago
    ).all()
    
    monthly_balance_change = sum(transaction.amount for transaction in monthly_transactions)
    
    # Count referrals
    referral_count = User.query.filter_by(referrer_id=current_user.id).count()
    
    # Prepare user dashboard context
    context = {
        'user': current_user,
        'recent_transactions': transactions,
        'referral_link': f"https://yoursite.com/register?ref={current_user.username}",
        'monthly_balance_change': monthly_balance_change,
        'referral_count': referral_count,
        'referral_bonus_per_signup': 10.00  # Example fixed bonus amount
    }
    
    return render_template('main/user_dashboard.html', **context)

@main_bp.route('/transactions')
@login_required
def transactions():
    """
    User transactions page with pagination.
    
    Returns:
        Rendered transactions template with user's transaction history
    """
    # Get page number from query parameter, default to 1
    page = request.args.get('page', 1, type=int)
    
    # Set up pagination
    per_page = 10  # Number of transactions per page
    
    # Paginate transactions for the current user
    pagination = Transaction.query.filter_by(user_id=current_user.id) \
        .order_by(Transaction.created_at.desc()) \
        .paginate(page=page, per_page=per_page, error_out=False)
    
    # Prepare context
    context = {
        'user': current_user,
        'transactions': pagination.items,
        'pagination': pagination
    }
    
    return render_template('transactions.html', **context)

@main_bp.route('/structure')
@login_required
def user_structure():
    """
    User referral structure page.
    
    Returns:
        Rendered structure template with user's referral network
    """
    # Fetch direct referrals
    direct_referrals = User.query.filter_by(referrer_id=current_user.id).all()
    
    # You might want to implement a more complex referral tree logic later
    context = {
        'user': current_user,
        'direct_referrals': direct_referrals
    }
    
    return render_template('structure.html', **context)

@main_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """
    Route to change user password.
    
    Returns:
        Rendered change password template or redirects after successful change
    """
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate password change
        if not current_user.check_password(current_password):
            flash('Current password is incorrect.', 'danger')
            return redirect(url_for('main.change_password'))
        
        if new_password != confirm_password:
            flash('New passwords do not match.', 'danger')
            return redirect(url_for('main.change_password'))
        
        # Update password
        current_user.set_password(new_password)
        db.session.commit()
        
        flash('Password changed successfully!', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('change_password.html')

@main_bp.route('/set_language/<lang>')
def set_language(lang):
    """
    Set the language for the current session.
    
    Args:
        lang (str): Language code (e.g., 'en', 'ru')
    
    Returns:
        Redirect to the previous page or landing page
    """
    # Validate language
    if lang in ['en', 'ru']:
        session['language'] = lang
    
    # Redirect to the previous page or landing page
    return redirect(request.referrer or url_for('main.landing'))

@main_bp.route('/deposit', methods=['GET', 'POST'])
@login_required
def deposit():
    """
    Route to handle user deposits.
    
    Returns:
        Rendered deposit template or redirects after successful deposit
    """
    if request.method == 'POST':
        amount = request.form.get('amount', type=float)
        
        if amount is None or amount <= 0:
            flash('Invalid deposit amount.', 'danger')
            return redirect(url_for('main.deposit'))
        
        try:
            # Add deposit transaction
            deposit_transaction = Transaction(
                user_id=current_user.id,
                amount=amount,
                description='Deposit',
                transaction_type='deposit'
            )
            
            # Update user balance
            current_user.balance += amount
            
            db.session.add(deposit_transaction)
            db.session.commit()
            
            flash(f'Successfully deposited ${amount:.2f}', 'success')
            return redirect(url_for('main.user_dashboard'))
        
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during deposit.', 'danger')
            # Log the error for debugging
            print(f"Deposit error: {e}")
    
    return render_template('deposit.html')

@main_bp.route('/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw():
    """
    Route to handle user withdrawals.
    
    Returns:
        Rendered withdraw template or redirects after successful withdrawal
    """
    if request.method == 'POST':
        amount = request.form.get('amount', type=float)
        
        if amount is None or amount <= 0:
            flash('Invalid withdrawal amount.', 'danger')
            return redirect(url_for('main.withdraw'))
        
        if amount > current_user.balance:
            flash('Insufficient funds.', 'danger')
            return redirect(url_for('main.withdraw'))
        
        try:
            # Add withdrawal transaction
            withdrawal_transaction = Transaction(
                user_id=current_user.id,
                amount=-amount,  # Negative amount to represent withdrawal
                description='Withdrawal',
                transaction_type='withdrawal'
            )
            
            # Update user balance
            current_user.balance -= amount
            
            db.session.add(withdrawal_transaction)
            db.session.commit()
            
            flash(f'Successfully withdrew ${amount:.2f}', 'success')
            return redirect(url_for('main.user_dashboard'))
        
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during withdrawal.', 'danger')
            # Log the error for debugging
            print(f"Withdrawal error: {e}")
    
    return render_template('withdraw.html')