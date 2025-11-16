from flask import Flask
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import os

bcrypt = Bcrypt()  
load_dotenv()

def create_app():
    app = Flask(
        __name__,
        template_folder='../templates',
        static_folder='../static'
    )


    bcrypt.init_app(app)

    app.secret_key = "clave_super_secreta_123"

    
    from .routes import main, tienda_bp, cuenta, close_db

    app.register_blueprint(main)
    app.register_blueprint(tienda_bp)
    app.register_blueprint(cuenta)
    app.config['GOOGLE_CLIENT_ID'] = os.getenv('GOOGLE_CLIENT_ID')
    app.config['GOOGLE_CLIENT_SECRET'] = os.getenv('GOOGLE_CLIENT_SECRET')
    app.config['FLASK_SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
    app.config['GOOGLE_REDIRECT_URI'] = os.getenv('GOOGLE_REDIRECT_URI', 'http://127.0.0.1:5000/auth/callback')
    os.environ.setdefault('OAUTHLIB_INSECURE_TRANSPORT', '1')
    app.teardown_appcontext(close_db)

    return app


