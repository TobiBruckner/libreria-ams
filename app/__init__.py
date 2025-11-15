from flask import Flask
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()  

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

    app.teardown_appcontext(close_db)

    return app


