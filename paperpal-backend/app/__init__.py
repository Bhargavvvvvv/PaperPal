from flask import Flask
from flask_cors import CORS
from config.config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    CORS(app, resources={
        r"/api/*": {
            "origins": Config.CORS_ORIGINS,
            "methods": ["OPTIONS", "GET", "POST"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    }, supports_credentials=True)

    from controller.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app