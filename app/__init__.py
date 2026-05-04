from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    login_manager.login_view = 'auth.login'

    # ADD THESE 3 LINES — temporary until Day 2 models are ready
    @login_manager.user_loader
    def load_user(user_id):
        return None

    from app.routes.auth import auth
    from app.routes.memory import memory
    from app.routes.share import share

    app.register_blueprint(auth)
    app.register_blueprint(memory)
    app.register_blueprint(share)

    return app