from flask import Flask, g
from app.extensions import db, bcrypt, login_manager
from app.routes import auth, general, admin
from app.models.user import create_default_admin
from flask_login import current_user

def create_app():
    app = Flask(__name__)
    # load config from config.py
    app.config.from_object('config.Config')

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    app.register_blueprint(auth.bp)
    app.register_blueprint(general.bp)
    app.register_blueprint(admin.bp)

    # Load the current user before each request 
    # for use in templating
    @app.before_request
    def load_user():
        g.user = current_user

    with app.app_context():
        # Create database tables if they don't exist
        db.create_all()
        # create default admin if not exists
        create_default_admin(
            default_username=app.config.get('DEFAULT_ADMIN_USER', 'admin'),
            default_password=app.config.get('DEFAULT_ADMIN_PASS', 'password')
        )

    return app