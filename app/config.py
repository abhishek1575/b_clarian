

import os
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "mysql+pymysql://root:Abhishekkhobe%40123@localhost/grocery")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwtsecretkey")







































# import os
# from dotenv import load_dotenv

# basedir = os.path.abspath(os.path.dirname(__file__))

# load_dotenv()

# class Config:
#     SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
#     SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "mysql+pymysql://root:admin123@localhost/grocery")
#     SQLALCHEMY_TRACK_MODIFICATIONS = False
#     JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwtsecretkey")
