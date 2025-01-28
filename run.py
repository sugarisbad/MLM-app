import sys
import os
import click
from app import create_app, db
from app.models import User
from flask.cli import with_appcontext

# Ensure the app directory is in the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Create the Flask application
app = create_app()

@app.cli.command('create-admin')
@click.option('--username', prompt='Enter admin username', help='Admin username')
@click.option('--password', prompt='Enter admin password', hide_input=True, confirmation_prompt=True, help='Admin password')
@with_appcontext
def create_admin_command(username, password):
    """Create a new admin user."""
    # Check if user already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        click.echo(f'Admin user {username} already exists!')
        return

    # Create new admin user
    admin = User(
        username=username,
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
    # Ensure the app runs in debug mode for development
    app.run(debug=True, host='0.0.0.0', port=5000)
