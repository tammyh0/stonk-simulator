from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, current_user
from flask_login.utils import login_required, logout_user
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash
from decimal import *
import requests
import math
import os


# Turn this program into a flask app
app = Flask(__name__)

# Configure app
app.config['SECRET_KEY'] = 'dev'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:yell0wsubmarine@localhost/stonks'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://ynvxhyomwjwsnj:beff12085f7ee6b8f56951161081a3291455fda11a7ffddda7fcb2de81a8264f@ec2-44-194-183-115.compute-1.amazonaws.com:5432/d39gm4e67mnnbd'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace("://", "ql://", 1)


# Create and initialize database
db = SQLAlchemy(app)



### MODELS ###

# Stores users' account information
class User(db.Model, UserMixin):
  __tablename__ = "user"

  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.Text, unique=True)
  password = db.Column(db.Text)
  cash = db.Column(db.Numeric(scale=2))
  holdings = db.relationship('Holding', backref='user', lazy=True)
  history = db.relationship('Transaction', backref='user', lazy=True)

# Stores users' current holdings 
class Holding(db.Model):
  __tablename__ = "holding"

  id = db.Column(db.Integer, primary_key=True)
  symbol = db.Column(db.Text)
  name = db.Column(db.Text)
  shares = db.Column(db.Integer)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Stores users' transaction history
class Transaction(db.Model):
  __tablename__ = "transaction"

  id = db.Column(db.Integer, primary_key=True)
  timestamp = db.Column(db.DateTime(timezone=True), default=func.now())
  symbol = db.Column(db.Text)
  name = db.Column(db.Text)
  price = db.Column(db.Numeric(scale=2))
  shares = db.Column(db.Integer)
  transaction_type = db.Column(db.Text)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)



### AUTH ROUTES ###

# Register new user
@app.route('/register', methods=['GET', 'POST'])
def register():
  error = None
  if request.method == 'POST':
    username = request.form.get('username')
    password = request.form.get('password')

    # Handle empty inputs
    if not username or not password:
      error = 'Please provide both a username and password'
    else: 
      # Check if user exists in database
      user = User.query.filter_by(username=username).first()
      if user:
        error = 'Username already exists. Try again.'
      else:
        # Create new user
        new_user = User(username=username, password=generate_password_hash(password, method='sha256'), cash=10000)

        # Add new user to database
        db.session.add(new_user)
        db.session.commit()

        # Automatically log in user
        login_user(new_user)

        # Send user to home page
        return redirect(url_for('home'))

  return render_template('auth/register.html', hideNav=True, hideSearch=False, error=error)


# Log in existing user
@app.route('/login', methods=['GET', 'POST'])
def login():
  error = None
  if request.method == 'POST':
    username = request.form.get('username')
    password = request.form.get('password')

    # Handle empty inputs
    if not username or not password:
      error = 'Please provide both a username and password'
    else: 
      # Check if user exists in database and if password is valid
      user = User.query.filter_by(username=username).first()
      if not user:
        error = 'Username does not exist'
      elif not check_password_hash(user.password, password):
        error = 'Incorrect password'
      else:
        # User has right credentials
        login_user(user)

        # Send user to home page
        return redirect(url_for('home'))

  return render_template('auth/login.html', hideNav=True, hideSearch=False,  error=error)


# Log out existing user
@app.route('/logout')
@login_required
def logout():
  logout_user()

  # Send user to login page
  return redirect(url_for('login'))



### MAIN VIEW ROUTES ###

# Show home page aka main dashboard
@app.route('/')
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

  return render_template('home/dash.html', username=username, hideSearch=False, total=twoDecPlaces(total), cash=cash, currentHoldings=currentHoldings)


# View searched stock's information
@app.route('/view', methods=['POST'])
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
@app.route('/buy', methods=['POST'])
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

  return render_template('home/dash.html', username=username, hideSearch=False, transactionSuccess=True, units=int(units), symbol=symbol, type="buy", total=twoDecPlaces(total), cash=cash, currentHoldings=currentHoldings)


# Sell stock
@app.route('/sell', methods=['POST'])
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

  return render_template('home/dash.html', username=username, hideSearch=False, transactionSuccess=True, units=int(units), symbol=symbol, type="sell", total=twoDecPlaces(total), cash=cash, currentHoldings=currentHoldings)


# View transaction history
@app.route('/history')
@login_required
def history():
  # Get transaction information
  username = current_user.username
  user = User.query.filter_by(username=username).first()

  transactions = Transaction.query.filter_by(user_id=user.id).order_by(Transaction.timestamp.desc())

  return render_template('history/transactions.html', username=username, transactions=transactions)



### ACCOUNT ROUTES ###

# View user account settings 
@app.route('/account')
@login_required
def user_account():
  username = current_user.username

  return render_template('settings/account.html', hideSearch=True, username=username)


# Reset user's cash to $10,000 and reset portfolio
@app.route('/reset', methods=['POST'])
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
  return redirect(url_for('home'))


# Delete user's account
@app.route('/delete', methods=['POST'])
@login_required
def delete():
  username = current_user.username
  user = User.query.filter_by(username=username).first()
  db.session.delete(user)
  db.session.commit()

  return redirect(url_for('login'))






### HELPER FUNCTIONS ###

# Get stock quote data from Finnhub API
def quoteData(symbol):
  url = f'https://finnhub.io/api/v1/quote?symbol={symbol}&token=c3nlhsaad3iabnjjd4c0'
  r = requests.get(url)
  status = r.status_code
  if status != 200:
    return 'error'
  else:
    data = r.json()
    if data:
      return data
    else:
      return 'empty data'


# Get basic financials data from Finnhub API
def financesData(symbol):
  url = f'https://finnhub.io/api/v1/stock/metric?symbol={symbol}&metric=all&token=c3nlhsaad3iabnjjd4c0'
  r = requests.get(url)
  status = r.status_code
  if status != 200:
    return 'error'
  else:
    data = r.json()
    if data["metric"]:
      return data["metric"]
    else:
      return 'empty data'


# Get company profile data from Finnhub API
def companyData(symbol):
  url = f'https://finnhub.io/api/v1/stock/profile2?symbol={symbol}&token=c3nlhsaad3iabnjjd4c0'
  r = requests.get(url)
  status = r.status_code
  if status != 200:
    return 'error'
  else:
    data = r.json()
    if data:
      return data
    else:
      return 'empty data'


# Get company overview data from Alphavantage API
def companyOverviewData(symbol):
  url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey=1ZZ8Y4Y0A7I7TSAP'
  r = requests.get(url)
  status = r.status_code
  if status != 200:
    return 'error'
  else:
    data = r.json()
    if data:
      if "Note" in data.keys():
        return 'empty data'
      else:
        return data
    else:
      return 'empty data'


# Get information about stock volume from Alphavantage API
def volumeData(symbol):
  url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=IBM&apikey=c3nlhsaad3iabnjjd4c0'
  r = requests.get(url)
  status = r.status_code
  if status != 200:
    return 'error'
  else:
    # Check if data is available for the stock symbol
    data = r.json()
    if data:
      if "Note" in data.keys():
        return 'empty data'
      elif data["Global Quote"]:
        return data["Global Quote"]
      else:
        return 'empty data'
    else:
      return 'empty data'


# Round number to two decimal places
def twoDecPlaces(value):
  if value:
    result = "{:.2f}".format(float(value))

    return result
  else:
    return value


# Shorten extremely large numbers
def millify(value):
  millnames = ['','k','M','B','T']
  if value:
    n = float(value)
    millidx = max(0,min(len(millnames)-1,
                        int(math.floor(0 if n == 0 else math.log10(abs(n))/3))))

    return '{:.2f}{}'.format(n / 10**(3 * millidx), millnames[millidx])
  else:
    return value



# Create, configure, and initialize login manager
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# Query user's ID from database for login manager to remember for sessions
@login_manager.user_loader
def load_user(user_id):
  return User.query.get(int(user_id))


# Automatically run and update app, and allow debug feature
if __name__ == "__main__":
  app.run(debug=False)