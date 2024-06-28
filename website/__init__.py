
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    # initialize app
    app = Flask(__name__)
    # app's secret key
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    # database location
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    # initialize database
    db.init_app(app)

    # import everything for the app
    from .auth import auth
    from .views import views
    from .models import User, Payment, Expense 


    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
 
    # create the database
    with app.app_context():
        db.create_all()

    # initiallize and create the login manager that will automatically handle logging in and out
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # loads the current user based on the id
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    # return the app so that main can use it
    return app

# function to create the database, checking if it already exists or not
def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
