from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

db = SQLAlchemy()

# User Model 
class User(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user") # user, admin, runner
    isActive = db.Column(db.Boolean, default=True)  # New field to track user activity  

    def to_dict(self):
        return {
        "id": self.id,
        "name": self.name,
        "email": self.email,
        "phone": self.phone,
        "role": self.role,
        "isActive": self.isActive,
        }

    
    addresses = db.relationship('Address', backref='user', lazy=True)
    orders = db.relationship('Order', backref='user', lazy=True)
    carts = db.relationship('Cart', backref='user', lazy=True)
    runner_assignments = db.relationship('RunnerAssignments', backref='runner', lazy=True, 
                                         foreign_keys='RunnerAssignments.runner_id')




class Address(db.Model):
    __tablename__ = 'address'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    street = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    zip_code = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(100), nullable=False)

# Product Model
class Product(db.Model):

    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(50), nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    category = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        return {
        "id": self.id,
        "name": self.name,
        "description": self.description,
        "category": self.category,
        "price": self.price,
        "unit": self.unit,
        "stock": self.stock,
        "image_url": self.image_url or ""
        }



# Cart Model 
class Cart(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    product = db.relationship('Product', backref=db.backref('carts', lazy=True))

# Order Model
class Order(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default="Pending")  # Pending, Processing, Out_for_delivery, Delivered, Cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships with related tables
    order_items = db.relationship('OrderItems', backref='order', lazy=True)
    payments = db.relationship('Payments', backref='order', lazy=True)
    runner_assignments = db.relationship('RunnerAssignments', backref='order', lazy=True)
    delivery_analytics = db.relationship('DeliveryAnalytics', backref='order', lazy=True, uselist=False)
    status_history = db.relationship('OrderStatusHistory', backref='order', lazy=True)

# Inventory Model 
class Inventory(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    product = db.relationship('Product', backref=db.backref('inventory', lazy=True))

# OrderItems Model (each record represents an item in an order)


class OrderItems(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_order_time = db.Column(db.Float, nullable=False)
    
    product = db.relationship('Product', backref=db.backref('order_items', lazy=True))

# RunnerAssignments Model 
class RunnerAssignments(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    runner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    picked_up_at = db.Column(db.DateTime, nullable=True)
    delivered_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(50), default="assigned")  # assigned, picked_up, delivered, cancelled

# Payments Model (tracks payment details for an order)
class Payments(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    payment_method = db.Column(db.String(30), nullable=False)
    transaction_id = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending")  # success, failed, pending
    paid_at = db.Column(db.DateTime, nullable=True)

# RunnerLocation Model (stores the current location of a runner/delivery agent)
class RunnerLocation(db.Model):
    
    runner_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    runner = db.relationship('User', backref=db.backref('runner_location', uselist=False))

# ===============================
# Analytics Models
# ===============================

# DeliveryAnalytics Model (tracks delivery time metrics for each order)
class DeliveryAnalytics(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    runner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    order_placed_at = db.Column(db.DateTime, nullable=False)
    order_picked_at = db.Column(db.DateTime, nullable=True)
    order_delivered_at = db.Column(db.DateTime, nullable=True)
# Track metrics such as product views, cart abandonment rates, and average cart size to optimize product offerings and user experience.
    @property
    def delivery_duration_minutes(self):
        if self.order_delivered_at and self.order_placed_at:
            return int((self.order_delivered_at - self.order_placed_at).total_seconds() / 60)
        return None

# OrderStatusHistory Model (logs every change in an order's status)
class OrderStatusHistory(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    old_status = db.Column(db.String(50), nullable=False)
    new_status = db.Column(db.String(50), nullable=False)
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)

# ProductViews Model (tracks when a product is viewed by a user)
class ProductViews(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    viewed_at = db.Column(db.DateTime, default=datetime.utcnow)

# ProductSales Model (aggregates daily sales data for each product)
class ProductSales(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity_sold = db.Column(db.Integer, nullable=False)
    total_revenue = db.Column(db.Float, nullable=False)
    recorded_on = db.Column(db.Date, default=date.today)
