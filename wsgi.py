import json

from dotenv import load_dotenv
from flasgger import Swagger
from flask import jsonify
from flask_swagger_ui import get_swaggerui_blueprint

from app import create_app
from config import Config

load_dotenv()

SWAGGER_URL = "/swagger"
API_URL = "/swagger.json"
app = create_app()

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={"app_name": "Moru Quiz Test"}
)


swagger = Swagger(app)


@app.route("/swagger.json")
def swagger_json():
    with open(Config.POSTMAN_COLLECTION, "r") as f:
        spec_dict = json.load(f)
    return jsonify(spec_dict)


app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)
