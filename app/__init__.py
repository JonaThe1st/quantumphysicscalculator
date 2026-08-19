from flask import Flask

from app.config import config_by_name


def create_app(config_name: str = "development") -> Flask:
    app = Flask(__name__)

    config_class = config_by_name.get(config_name, config_by_name["development"])
    app.config.from_object(config_class)

    from app.routes.api import api_bp
    from app.routes.pages import pages_bp

    app.register_blueprint(pages_bp)
    app.register_blueprint(api_bp)

    return app