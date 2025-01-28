import os
import sys
import click
from flask.cli import FlaskGroup

# Ensure the app directory is in the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.models import User

def create_flask_app():
    """Create and return a Flask application instance."""
    return create_app()

@click.group(cls=FlaskGroup, create_app=create_flask_app)
def cli():
    """Management script for the Web application."""
    pass

@cli.command('create-admin')
@click.option('--username', prompt='Enter admin username', help='Admin username')
@click.option('--email', prompt='Enter admin email', help='Admin email')
@click.option('--password', prompt='Enter admin password', hide_input=True, confirmation_prompt=True, help='Admin password')
def create_admin_command(username, email, password):
    """Create a new admin user."""
    app = create_app()
    with app.app_context():
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            click.echo(f'Admin user {username} already exists!')
            return

        # Create new admin user
        admin = User(
            username=username, 
            email=email,
            is_admin=True
        )
        admin.set_password(password)
        
        try:
            db.session.add(admin)
            db.session.commit()
            click.echo(f'Admin user {username} created successfully!')
        except Exception as e:
            db.session.rollback()
            click.echo(f'Error creating admin user: {str(e)}')

if __name__ == '__main__':
    cli()