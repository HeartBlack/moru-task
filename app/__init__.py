import pkg_resources
from flask import Flask, jsonify
from flask_migrate import Migrate

from app.extensions import db
from app.main import bp as main_bp
from config import Config

migrate = Migrate()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config["DEBUG"] = True
    app.config.from_object(config_class)
    app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies"]
    app.config["JWT_SECRET_KEY"] = Config.SECRET_KEY

    db.init_app(app)
    migrate.init_app(app, db)
    app.register_blueprint(main_bp, url_prefix="/api/v1")

    @app.route("/")
    def test_page():
        installed_packages = pkg_resources.working_set
        installed_packages_list = sorted(
            ["%s==%s" % (i.key, i.version) for i in installed_packages]
        )
        html_output = "<h1>All Installed packages </h1><br>"

        for package in installed_packages_list:
            html_output += f"<li>{package}</li></br>"

        return html_output

    return app
