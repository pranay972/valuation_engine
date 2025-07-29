"""
Flask application factory for the valuation backend.
"""

from flask import Flask
from flask_cors import CORS
import os


def create_app(test_config=None):
    """Application factory pattern for Flask app."""
    app = Flask(__name__, instance_relative_config=True)
    
    # Configure CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Default configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        DEBUG=os.environ.get('FLASK_DEBUG', 'True').lower() == 'true',
    )

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.update(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Register blueprints
    from app.api import valuation
    from app.swagger import swagger_ui_blueprint
    
    app.register_blueprint(valuation.bp)
    app.register_blueprint(swagger_ui_blueprint)

    @app.route('/health')
    def health_check():
        """Health check endpoint."""
        return {'status': 'healthy', 'message': 'Valuation API is running'}

    @app.route('/static/swagger.json')
    def swagger_json():
        """Serve the Swagger JSON specification."""
        return app.send_static_file('swagger.json')

    return app 