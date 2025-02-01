from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
import pyodbc

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Database Configuration
DB_USERNAME = os.getenv('DB_USERNAME', 'sa')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'sa123')
DB_SERVER = os.getenv('DB_SERVER', 'Karekar')
DB_DATABASE = os.getenv('DB_DATABASE', '4K')

if not all([DB_USERNAME, DB_PASSWORD, DB_SERVER, DB_DATABASE]):
    raise ValueError("Database environment variables are not properly set!")

app.config['SQLALCHEMY_DATABASE_URI'] = f"mssql+pyodbc://{DB_USERNAME}:{DB_PASSWORD}@{DB_SERVER}/{DB_DATABASE}?driver=ODBC+Driver+17+for+SQL+Server"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class MenuItem(db.Model):
    __tablename__ = 'menu_items'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    total_price = db.Column(db.Float, nullable=False)
    payment_status = db.Column(db.String(20), default="PENDING")
    created_at = db.Column(db.DateTime, default=db.func.now())

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    order = db.relationship('Order', backref='items')
    menu_item = db.relationship('MenuItem')

# Routes
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/menu', methods=['GET'])
def get_menu():
    try:
        menu = MenuItem.query.all()
        return jsonify([{"id": item.id, "category": item.category, "name": item.name, "price": item.price} for item in menu]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/order', methods=['POST'])
def create_order():
    try:
        data = request.json
        items = data.get('items', [])

        if not items:
            return jsonify({"error": "No items provided in the order"}), 400

        total_price = 0
        for item in items:
            menu_item = MenuItem.query.get(item['id'])
            if not menu_item:
                return jsonify({"error": f"Menu item with ID {item['id']} not found"}), 404
            total_price += item['quantity'] * menu_item.price

        order = Order(total_price=total_price)
        db.session.add(order)
        db.session.commit()

        for item in items:
            order_item = OrderItem(order_id=order.id, menu_item_id=item['id'], quantity=item['quantity'])
            db.session.add(order_item)

        db.session.commit()
        return jsonify({"order_id": order.id, "total_price": total_price}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/order/<int:order_id>/pay', methods=['POST'])
def pay_order(order_id):
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({"error": "Order not found"}), 404

        order.payment_status = 'PAID'
        db.session.commit()
        return jsonify({"message": "Payment successful"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/order/<int:order_id>', methods=['GET'])
def get_order(order_id):
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({"error": "Order not found"}), 404

        result = {
            "order_id": order.id,
            "total_price": order.total_price,
            "payment_status": order.payment_status,
            "items": [
                {
                    "name": item.menu_item.name,
                    "price": item.menu_item.price,
                    "quantity": item.quantity,
                } for item in order.items
            ],
        }
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
