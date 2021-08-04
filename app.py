from flask import Flask
from flask_login import LoginManager
from models import db, User


# Turn this program into a flask app
app = Flask(__name__)


# Configure app
app.config['SECRET_KEY'] = 'dev'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:yell0wsubmarine@localhost/stonks'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://ynvxhyomwjwsnj:beff12085f7ee6b8f56951161081a3291455fda11a7ffddda7fcb2de81a8264f@ec2-44-194-183-115.compute-1.amazonaws.com:5432/d39gm4e67mnnbd'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace("://", "ql://", 1)


# Import blueprints
from auth import auth
from account import account
from main_views import main_views

# Register blueprints
app.register_blueprint(auth, url_prefix='/')
app.register_blueprint(account, url_prefix='/')
app.register_blueprint(main_views, url_prefix='/')


# Initialize database
db.init_app(app)


# Create, configure, and initialize login manager
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)


# Query user's ID from database for login manager to remember for sessions
@login_manager.user_loader
def load_user(user_id):
  return User.query.get(int(user_id))


# Automatically run and update app, and allow debug feature
if __name__ == "__main__":
  app.run(debug=False)