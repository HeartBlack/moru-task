import os

from dotenv import load_dotenv

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "aaklghkashghalghlashgahslghlahgl")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    POSTMAN_COLLECTION = "swagger.json"
