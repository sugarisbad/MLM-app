from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from . import db  # Import db from app/__init__.py

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    balance = db.Column(db.Float, default=0.0)
    is_admin = db.Column(db.Boolean, default=False)
    referrer_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'), nullable=True)
    referrals = db.relationship('User', backref=db.backref('referrer', remote_side=[id]))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    transactions = db.relationship('Transaction', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        """Set a secure password hash."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password is correct."""
        return check_password_hash(self.password_hash, password)
    
    def add_transaction(self, amount, description):
        """
        Add a transaction for the user.
        
        Args:
            amount (float): Transaction amount
            description (str): Transaction description
        """
        transaction = Transaction(user_id=self.id, amount=amount, description=description)
        db.session.add(transaction)
        db.session.commit()
    
    def get_referral_bonus(self, amount, level):
        """
        Calculate referral bonus based on transaction amount and level.
        
        Args:
            amount (float): Base transaction amount
            level (int): Referral level
        
        Returns:
            float: Calculated referral bonus
        """
        settings = ReferralSettings.query.filter_by(level=level).first()
        return amount * (settings.percentage / 100) if settings else 0

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Transaction {self.id}: {self.amount} - {self.description}>'

class ReferralSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.Integer, nullable=False, unique=True)
    percentage = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<ReferralSettings Level {self.level}: {self.percentage}%>'
    
    @classmethod
    def initialize_default_settings(cls):
        """
        Initialize default referral settings if not already set.
        """
        if cls.query.count() == 0:
            default_settings = [
                {'level': 1, 'percentage': 5.0},
                {'level': 2, 'percentage': 3.0},
                {'level': 3, 'percentage': 1.0}
            ]
            
            for setting in default_settings:
                ref_setting = cls(level=setting['level'], percentage=setting['percentage'])
                db.session.add(ref_setting)
            
            db.session.commit()