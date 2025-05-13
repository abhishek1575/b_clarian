from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate 
from app.config import Config 
from app.models import db
import os


app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

db.init_app(app)
jwt = JWTManager(app)
migrate = Migrate(app, db) 


app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'img')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


from app.order import order_bp
from app.auth import auth_bp  
from app.product import product_bp
from app.admin import admin_bp
from app.cart import cart_bp
from app.address import address_bp
from app.delivery_boy import runner_bp

app.register_blueprint(order_bp)
app.register_blueprint(address_bp)
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(product_bp, url_prefix='/api')
# app.register_blueprint(product_bp, url_prefix='/products')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(cart_bp)
app.register_blueprint(runner_bp, url_prefix='/runner')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

