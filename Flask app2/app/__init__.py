import logging
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
import os

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[
        logging.StreamHandler()  # Logs to stdout for Heroku
    ]
)
logger = logging.getLogger(__name__)
logger.debug("Starting Flask app initialization")

# Initialize SQLAlchemy
db = SQLAlchemy()

# Load environment variables
load_dotenv()
logger.debug("Loaded environment variables")

def create_app():
    logger.debug("Entering create_app")
    app = Flask(__name__)

    # Configure Flask
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    logger.debug(f"Set SQLALCHEMY_DATABASE_URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

    # Test database connection
    logger.debug("Attempting database connection")
    try:
        engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
        engine.connect()
        logger.debug("Database connection successful")
    except OperationalError as e:
        logger.error(f"Database connection failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during database connection: {e}")
        raise

    # Initialize database
    logger.debug("Initializing SQLAlchemy")
    try:
        db.init_app(app)
        logger.debug("SQLAlchemy initialized")
    except Exception as e:
        logger.error(f"SQLAlchemy initialization failed: {e}")
        raise

    # Create tables
    logger.debug("Creating database tables")
    with app.app_context():
        try:
            db.create_all()
            logger.debug("Database tables created")
        except Exception as e:
            logger.error(f"Table creation failed: {e}")
            raise

    # Enable CORS
    CORS(app)
    logger.debug("CORS enabled")

    # Log all requests and responses
    @app.before_request
    def log_request():
        logger.debug(f"BACKEND REQUEST: {request.method} {request.url}")
        logger.debug(f"Headers: {dict(request.headers)}")
        logger.debug(f"Query Params: {request.args.to_dict()}")
        if request.is_json:
            logger.debug(f"Body: {request.get_json(silent=True)}")

    @app.after_request
    def log_response(response):
        logger.debug(f"BACKEND RESPONSE: Status {response.status_code}")
        if response.is_json:
            try:
                logger.debug(f"Response Body: {response.get_json(silent=True)}")
            except Exception as e:
                logger.error(f"Failed to parse response JSON: {e}")
        return response

    @app.errorhandler(Exception)
    def handle_error(error):
        logger.error(f"BACKEND ERROR in {request.path}: {str(error)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

    # Register blueprints
    logger.debug("Registering blueprints")
    try:
        from app.controllers.item_controller import item_bp
        from app.controllers.customer_controller import customer_bp
        from app.controllers.pickMargin_controller import pickMargin_bp
        from app.controllers.card_controller import card_bp
        from app.controllers.WIP_quotation_controller import wip_quotation_bp
        from app.controllers.FinalQuotation_controller import final_quotation_bp
        from app.controllers.DownloadPDF import download_quotation_bp
        from app.controllers.SharePdf import share_quotation_bp

        app.register_blueprint(item_bp, url_prefix="/api/items")
        app.register_blueprint(customer_bp, url_prefix="/api")
        app.register_blueprint(pickMargin_bp, url_prefix="/api")
        app.register_blueprint(card_bp, url_prefix="/api")
        app.register_blueprint(wip_quotation_bp, url_prefix="/api")
        app.register_blueprint(final_quotation_bp, url_prefix="/api")
        app.register_blueprint(download_quotation_bp, url_prefix="/api")
        app.register_blueprint(share_quotation_bp, url_prefix="/api")
        logger.debug("Blueprints registered successfully")
    except ImportError as e:
        logger.error(f"Failed to import blueprints: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to register blueprints: {e}")
        raise

    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health():
        logger.debug("Health check endpoint called")
        try:
            db.session.execute('SELECT 1')
            logger.debug("Database query successful")
            return jsonify({"status": "healthy", "database": "connected"}), 200
        except Exception as e:
            logger.error(f"Health check database query failed: {e}")
            return jsonify({"status": "unhealthy", "error": str(e)}), 500

    logger.debug("Flask app created successfully")
    return app