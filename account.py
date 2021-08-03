from models import db, User, Holding, Transaction

from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user
from flask_login.utils import login_required


# Create blueprint
account = Blueprint('account', __name__)


# View user account settings 
@account.route('/account')
@login_required
def user_account():
  username = current_user.username

  return render_template('settings/account.html', hideSearch=True, username=username)


# Reset user's cash to $10,000 and reset portfolio
@account.route('/reset', methods=['POST'])
@login_required
def reset():
  # Reset cash
  username = current_user.username
  user = User.query.filter_by(username=username).first()
  user.cash = 10000
  db.session.commit()

  # Reset portfolio, including all current holdings transaction history
  portfolio = Holding.query.filter_by(user_id=user.id).all()
  for holding in portfolio:
    db.session.delete(holding)
    db.session.commit()

  transactions = Transaction.query.filter_by(user_id=user.id).all()
  for transaction in transactions:
    db.session.delete(transaction)
    db.session.commit()

  # Send to home page showing updated cash amount
  return redirect(url_for('main_views.home'))


# Delete user's account
@account.route('/delete', methods=['POST'])
@login_required
def delete():
  username = current_user.username
  user = User.query.filter_by(username=username).first()
  db.session.delete(user)
  db.session.commit()

  return redirect(url_for('auth.login'))