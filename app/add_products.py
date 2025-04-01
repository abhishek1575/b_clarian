import sys
sys.path.append("..")
from app import app, db
from models import Product  # Adjust the import based on your project structure

# Define product data (Grocery & Dairy Products)
products = [
    # Groceries
    {"name": "Rice", "category": "Grocery", "price": 50, "stock": 100, "unit": "kg"},
    {"name": "Wheat Flour", "category": "Grocery", "price": 45, "stock": 80, "unit": "kg"},
    {"name": "Pulses", "category": "Grocery", "price": 100, "stock": 60, "unit": "kg"},
    {"name": "Sugar", "category": "Grocery", "price": 40, "stock": 90, "unit": "kg"},
    {"name": "Salt", "category": "Grocery", "price": 20, "stock": 200, "unit": "kg"},
    {"name": "Cooking Oil", "category": "Grocery", "price": 150, "stock": 70, "unit": "litre"},
    {"name": "Spices Pack", "category": "Grocery", "price": 250, "stock": 50, "unit": "pack"},
    {"name": "Tea Powder", "category": "Grocery", "price": 120, "stock": 60, "unit": "pack"},
    {"name": "Coffee", "category": "Grocery", "price": 180, "stock": 50, "unit": "pack"},
    {"name": "Instant Noodles", "category": "Grocery", "price": 25, "stock": 150, "unit": "pack"},
    
    # Dairy Products
    {"name": "Milk", "category": "Dairy", "price": 60, "stock": 100, "unit": "litre"},
    {"name": "Butter", "category": "Dairy", "price": 200, "stock": 40, "unit": "pack"},
    {"name": "Cheese", "category": "Dairy", "price": 250, "stock": 30, "unit": "pack"},
    {"name": "Curd", "category": "Dairy", "price": 50, "stock": 80, "unit": "litre"},
    {"name": "Paneer", "category": "Dairy", "price": 300, "stock": 40, "unit": "kg"},
    {"name": "Ghee", "category": "Dairy", "price": 600, "stock": 30, "unit": "litre"},
    {"name": "Condensed Milk", "category": "Dairy", "price": 150, "stock": 20, "unit": "can"},
    {"name": "Flavored Yogurt", "category": "Dairy", "price": 80, "stock": 50, "unit": "cup"},
    {"name": "Margarine", "category": "Dairy", "price": 180, "stock": 20, "unit": "pack"},
    {"name": "Whipping Cream", "category": "Dairy", "price": 350, "stock": 25, "unit": "litre"},
]

# Insert products into the database
with app.app_context():
    for item in products:
        product = Product(
            name=item["name"],
            category=item["category"],
            price=item["price"],
            stock=item["stock"],
            unit=item["unit"]
        )
        db.session.add(product)
    
    db.session.commit()
    print("Products added successfully!")
