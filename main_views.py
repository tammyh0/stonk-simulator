from models import db, User, Holding, Transaction
from helpers import quoteData, twoDecPlaces, financesData, companyData, companyOverviewData, volumeData, millify

from flask import Blueprint, request, render_template
from flask_login import current_user
from flask_login.utils import login_required
from decimal import *


# Create blueprint
main_views = Blueprint('main_views', __name__)


# Show home page aka main dashboard
@main_views.route('/')
@login_required
def home():
  username = current_user.username

  # Get grand total and current prices for holdings
  user = User.query.filter_by(username=username).first()
  cash = user.cash
  total = float(cash)
  currentHoldings = []
  holdings = Holding.query.filter_by(user_id=user.id)
  for holding in holdings:
    currentPrice = quoteData(holding.symbol)['c']
    holdingTotal = currentPrice * holding.shares
    total += holdingTotal

    name = holding.name
    symbol = holding.symbol
    shares = holding.shares
    currentHolding = {
      "name": name,
      "symbol": symbol,
      "shares": shares,
      "price": twoDecPlaces(currentPrice)
    }

    currentHoldings.append(currentHolding)

  return render_template('home/dash.html', username=username, hideSearch=False, total=twoDecPlaces(total), cash=twoDecPlaces(cash), currentHoldings=currentHoldings)


# View searched stock's information
@main_views.route('/view', methods=['POST'])
@login_required
def view():
  error = None

  stock_symbol = request.form.get("stock").split(' ')[0].upper()

  # Get Quote data from Finnhub API
  quoteInfo = quoteData(stock_symbol)
  if quoteInfo == 'error':
    error = True

  # Get Basic Financials data from Finnhub API
  financesInfo = financesData(stock_symbol)
  if financesInfo == 'error':
    error = True

  # Get Company Profile data from Finnhub API
  companyInfo = companyData(stock_symbol)
  if companyInfo == 'error':
    error = True

  # Get Company Overview data from Alphavantage API
  companyOverviewInfo = companyOverviewData(stock_symbol)
  if companyOverviewInfo == 'error':
    error = True

  # Get information about stock volume from Alphavantage API
  volumeInfo = volumeData(stock_symbol)
  if volumeInfo == 'error':
    error = True

  # Get username 
  username = current_user.username

  # Check if user currently owns this stock
  user = User.query.filter_by(username=username).first()
  stock = Holding.query.filter_by(user_id=user.id, symbol=stock_symbol).first()
  hasStock = False
  shares = 0
  if stock:
    hasStock = True
    # Get how many shares the user has of this stock
    shares = stock.shares

  # Get user's current cash amount
  cash = user.cash

  return render_template('stock/overview.html', error=error, stock=stock_symbol, username=username,
  quoteInfo=quoteInfo, financesInfo=financesInfo, companyInfo=companyInfo, companyOverviewInfo=companyOverviewInfo, volumeInfo=volumeInfo,
  twoDecPlaces=twoDecPlaces, millify=millify, hideSearch=False, hasStock=hasStock, cash=cash, shares=shares)


# Buy stock
@main_views.route('/buy', methods=['POST'])
@login_required
def buy():
  username = current_user.username
  units = float(request.form.get('units'))
  symbol = request.form.get('symbol')
  name = request.form.get('name')
  price = float(request.form.get('price'))

  # Update user's cash
  totalPrice = Decimal(units * price)
  user = User.query.filter_by(username=username).first()
  updatedCash = user.cash - totalPrice
  user.cash = updatedCash
  db.session.commit()

  # Update or add new holding for that user
  if Holding.query.filter_by(user_id=user.id, symbol=symbol).first():
    # Update this holding
    holding = Holding.query.filter_by(user_id=user.id, symbol=symbol).first()
    updatedShares = int(units) + holding.shares
    holding.shares = updatedShares
    db.session.commit()
  else:
    # Add a new holding
    new_holding = Holding(symbol=symbol, name=name, shares=units, user_id=user.id)
    db.session.add(new_holding)
    db.session.commit()

  # Update transaction history for that user
  new_transaction = Transaction(symbol=symbol, name=name, price=price, shares=units, transaction_type="buy", user_id=user.id)
  db.session.add(new_transaction)
  db.session.commit()

  username = current_user.username

  # Get grand total and current prices for holdings
  user = User.query.filter_by(username=username).first()
  cash = user.cash
  total = float(cash)
  currentHoldings = []
  holdings = Holding.query.filter_by(user_id=user.id)
  for holding in holdings:
    currentPrice = quoteData(holding.symbol)['c']
    holdingTotal = currentPrice * holding.shares
    total += holdingTotal

    name = holding.name
    symbol = holding.symbol
    shares = holding.shares
    currentHolding = {
      "name": name,
      "symbol": symbol,
      "shares": shares,
      "price": twoDecPlaces(currentPrice)
    }

    currentHoldings.append(currentHolding)

  return render_template('home/dash.html', username=username, hideSearch=False, transactionSuccess=True, units=int(units), symbol=symbol, type="buy", total=twoDecPlaces(total), cash=twoDecPlaces(cash), currentHoldings=currentHoldings)


# Sell stock
@main_views.route('/sell', methods=['POST'])
@login_required
def sell():
  username = current_user.username
  units = float(request.form.get('units'))
  symbol = request.form.get('symbol')
  name = request.form.get('name')
  price = float(request.form.get('price'))

  # Update user's cash
  totalPrice = Decimal(units * price)
  user = User.query.filter_by(username=username).first()
  updatedCash = user.cash + totalPrice
  user.cash = updatedCash
  db.session.commit()

  # Update holding
  holding = Holding.query.filter_by(user_id=user.id, symbol=symbol).first()
  updatedShares = holding.shares - int(units)
  holding.shares = updatedShares
  if holding.shares == 0:
    db.session.delete(holding)
  db.session.commit()

  # Update transaction history for that user
  new_transaction = Transaction(symbol=symbol, name=name, price=price, shares=units, transaction_type="sell", user_id=user.id)
  db.session.add(new_transaction)
  db.session.commit()

  username = current_user.username

  # Get grand total and current prices for holdings
  user = User.query.filter_by(username=username).first()
  cash = user.cash
  total = float(cash)
  currentHoldings = []
  holdings = Holding.query.filter_by(user_id=user.id)
  for holding in holdings:
    currentPrice = quoteData(holding.symbol)['c']
    holdingTotal = currentPrice * holding.shares
    total += holdingTotal

    name = holding.name
    symbol = holding.symbol
    shares = holding.shares
    currentHolding = {
      "name": name,
      "symbol": symbol,
      "shares": shares,
      "price": twoDecPlaces(currentPrice)
    }

    currentHoldings.append(currentHolding)

  return render_template('home/dash.html', username=username, hideSearch=False, transactionSuccess=True, units=int(units), symbol=symbol, type="sell", total=twoDecPlaces(total), cash=twoDecPlaces(cash), currentHoldings=currentHoldings)


# View transaction history
@main_views.route('/history')
@login_required
def history():
  # Get transaction information
  username = current_user.username
  user = User.query.filter_by(username=username).first()

  transactions = Transaction.query.filter_by(user_id=user.id).order_by(Transaction.timestamp.desc())

  return render_template('history/transactions.html', username=username, transactions=transactions)
