import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///dev.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DESCOPE_PROJECT_ID = os.getenv("DESCOPE_PROJECT_ID", "")
    DESCOPE_MANAGEMENT_KEY = os.getenv("DESCOPE_MANAGEMENT_KEY", "")
    DESCOPE_BASE_URL = os.getenv("DESCOPE_BASE_URL", "https://api.descope.com")
    DESCOPE_MOCK = os.getenv("DESCOPE_MOCK", "0") == "1"
