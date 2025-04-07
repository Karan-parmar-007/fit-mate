from flask import Flask
import os
from pymongo import MongoClient  # Import MongoClient for MongoDB
# from app.cron.scheduler import init_scheduler
from flask_cors import CORS
from app.utils.logger import logger
from app.cron.scheduler import init_scheduler


def create_app():
    app = Flask(__name__)
    
    # Load MongoDB configuration from environment variables
    app.config['MONGO_URI'] = os.getenv("MONGO_URI")
    app.config['MONGO_DBNAME'] = os.getenv("MONGO_DBNAME", "your_default_database")  # Set a default or adjust as needed

    # Initialize MongoDB client and attach to app
    if app.config['MONGO_URI']:
        app.mongo = MongoClient(app.config['MONGO_URI'])
    else:
        logger.error("MONGO_URI not set in environment variables.")
        raise ValueError("MONGO_URI must be set to connect to MongoDB.")

    # Configure OAuth client settings
    app.config['GOOGLE_CLIENT_ID'] = os.getenv("GOOGLE_CLIENT_ID")
    app.config['GOOGLE_CLIENT_SECRET'] = os.getenv("GOOGLE_CLIENT_SECRET")
    app.secret_key = os.getenv("SECRET_KEY", "your_default_secret_key")  # Ensure SECRET_KEY is set

    # Initialize OAuth with the Flask app

    # Enable CORS
    CORS(app, origins=["http://localhost:3000"], supports_credentials=True)

    # Register Blueprints
    from app.blueprints.user import user_bp
    from app.blueprints.exercise import exercise_bp
    from app.blueprints.daily import daily_bp
    from app.blueprints.gemini import gemini_bp

    from app.blueprints.sub_exercise import sub_exercise_bp


    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(exercise_bp, url_prefix='/api/exercise')
    app.register_blueprint(daily_bp, url_prefix='/api/daily')
    app.register_blueprint(sub_exercise_bp, url_prefix='/api/sub_exercise')
    app.register_blueprint(gemini_bp, url_prefix='/api/gemini')
    
    

    # Initialize scheduler within app context
    with app.app_context():
        logger.info("Initializing scheduler...")
        init_scheduler(app)
        logger.info("Scheduler initialized successfully!")

    # Log registered URLs for debugging
    logger.info("Registered URLs:")
    for rule in app.url_map.iter_rules():
        logger.info(rule)

    return app