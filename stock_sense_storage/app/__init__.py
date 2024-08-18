from flask import Flask
from app.utils.config import Config
from app.utils.database import db, migrate
from app.api.stock_quotes import stock_quotes_bp
from app.api.predictions import predictions_bp
from app.api.health_check import health_check_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(stock_quotes_bp, url_prefix='/api/stock_quotes')
    app.register_blueprint(predictions_bp, url_prefix='/api/predictions')
    app.register_blueprint(health_check_bp, url_prefix='/api/health_check')

    return app
