from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()

def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    if config_name == 'production':
        app.config.from_object('app.config.ProductionConfig')
    elif config_name == 'testing':
        app.config.from_object('app.config.TestingConfig')
    else:
        app.config.from_object('app.config.DevelopmentConfig')
    
    # Configure Flask to handle trailing slashes
    app.url_map.strict_slashes = False
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    
    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Register blueprints
    from app.api.analysis import analysis_bp
    from app.api.valuation import valuation_bp
    from app.api.results import results_bp
    from app.api.csv import csv_bp
    
    app.register_blueprint(analysis_bp, url_prefix='/api/analysis')
    app.register_blueprint(valuation_bp, url_prefix='/api/valuation')
    app.register_blueprint(results_bp, url_prefix='/api/results')
    app.register_blueprint(csv_bp, url_prefix='/api/csv')
    
    # Swagger UI registration
    try:
        from swagger import swagger_ui_blueprint
        app.register_blueprint(swagger_ui_blueprint)
    except Exception as e:
        # Swagger is optional; avoid crashing app if unavailable
        pass
    
    # Serve OpenAPI specification from backend/static/swagger.json
    backend_root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    swagger_static_dir = os.path.join(backend_root_dir, 'static')

    @app.route('/static/swagger.json', methods=['GET'])
    def swagger_json():
        return send_from_directory(swagger_static_dir, 'swagger.json')
    
    # Basic health endpoint
    @app.route('/health', methods=['GET'])
    def health():
        return {"status": "healthy"}
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app 