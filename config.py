

import os
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "mysql+pymysql://root:Abhishekkhobe%40123@localhost/grocery")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwtsecretkey")

    # UPLOAD_FOLDER = os.path.join('static', 'uploads')
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'uploads')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # app = Flask(__name__, static_url_path='/static', static_folder='static')
    # CORS(app)


