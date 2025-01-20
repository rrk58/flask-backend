from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Database configuration
DB_USERNAME = os.getenv('DB_USERNAME', 'sa')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'sa123')
DB_SERVER = os.getenv('DB_SERVER', 'Karekar')
DB_DATABASE = os.getenv('DB_DATABASE', '4K')

app.config['SQLALCHEMY_DATABASE_URI'] = f"mssql+pyodbc://{DB_USERNAME}:{DB_PASSWORD}@{DB_SERVER}/{DB_DATABASE}?driver=ODBC+Driver+17+for+SQL+Server"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class MenuItem(db.Model):
    __tablename__ = 'menu_items'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50))
    name = db.Column(db.String(100))
    price = db.Column(db.Float)

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    total_price = db.Column(db.Float)
    payment_status = db.Column(db.String(20), default="PENDING")
    created_at = db.Column(db.DateTime, default=db.func.now())

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'))
    quantity = db.Column(db.Integer)
    order = db.relationship('Order', backref='items')
    menu_item = db.relationship('MenuItem')

# Initialize the database
@app.before_first_request
def create_tables():
    db.create_all()

# Endpoints
@app.route('/menu', methods=['GET'])
def get_menu():
    menu = MenuItem.query.all()
    return jsonify([{"id": item.id, "category": item.category, "name": item.name, "price": item.price} for item in menu]), 200

@app.route('/order', methods=['POST'])
def create_order():
    data = request.json
    items = data.get('items', [])
    total_price = sum(item['quantity'] * item['price'] for item in items)
    order = Order(total_price=total_price)
    db.session.add(order)
    db.session.commit()
    for item in items:
        order_item = OrderItem(order_id=order.id, menu_item_id=item['id'], quantity=item['quantity'])
        db.session.add(order_item)
    db.session.commit()
    return jsonify({"order_id": order.id, "total_price": total_price}), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
