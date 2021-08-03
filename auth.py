from models import db, User

from flask import Blueprint, request, render_template, redirect, url_for
from flask_login import login_user
from flask_login.utils import login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash


# Create blueprint
auth = Blueprint('auth', __name__)


# Register new user
@auth.route('/register', methods=['GET', 'POST'])
def register():
  error = None

  # Handle submitted registration form
  if request.method == 'POST':

    # Get user inputs
    username = request.form.get('username')
    password = request.form.get('password')

    # Input(s) are empty
    if not username or not password:
      error = 'Please provide both a username and password'

    # Inputs aren't empty
    else: 
      user = User.query.filter_by(username=username).first()
      # Username already taken
      if user:
        error = 'Username already exists. Try again.'

      # Username valid
      else:
        # Add new user to database
        new_user = User(username=username, password=generate_password_hash(password, method='sha256'), cash=10000)
        db.session.add(new_user)
        db.session.commit()

        # Automatically log in user
        login_user(new_user)

        # Direct user to home page
        return redirect(url_for('main_views.home'))

  return render_template('auth/register.html', hideNav=True, hideSearch=False, error=error)


# Log in existing user
@auth.route('/login', methods=['GET', 'POST'])
def login():
  error = None

  # Handle submitted login form
  if request.method == 'POST':
    username = request.form.get('username')
    password = request.form.get('password')

    # Input(s) are empty
    if not username or not password:
      error = 'Please provide both a username and password'
    
    # Inputs aren't empty
    else: 
      # Check if user exists in database and if password is valid
      user = User.query.filter_by(username=username).first()
      if not user:
        error = 'Username does not exist'
      elif not check_password_hash(user.password, password):
        error = 'Incorrect password'

      # User has right credentials
      else:
        # Log user in
        login_user(user)

        # Send user to home page
        return redirect(url_for('main_views.home'))

  return render_template('auth/login.html', hideNav=True, hideSearch=False,  error=error)


# Log out existing user
@auth.route('/logout')
@login_required
def logout():
  logout_user()

  # Send user to login page
  return redirect(url_for('auth.login'))