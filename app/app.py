from flask import Flask, render_template, jsonify, request
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time
import os

app = Flask(__name__)

# ---------- Prometheus metrics ----------
REQUEST_COUNT = Counter(
    'app_request_count_total',
    'Total number of requests',
    ['method', 'endpoint', 'status']
)
REQUEST_LATENCY = Histogram(
    'app_request_latency_seconds',
    'Request latency in seconds',
    ['endpoint']
)
ORDER_COUNT = Counter(
    'app_orders_total',
    'Total number of orders placed'
)

# ---------- Sample product data ----------
PRODUCTS = [
    {"id": 1, "name": "Wireless Headphones", "price": 2999, "stock": 50, "category": "Electronics"},
    {"id": 2, "name": "Running Shoes",       "price": 1499, "stock": 30, "category": "Footwear"},
    {"id": 3, "name": "Backpack",             "price": 899,  "stock": 75, "category": "Bags"},
    {"id": 4, "name": "Smart Watch",          "price": 4999, "stock": 20, "category": "Electronics"},
    {"id": 5, "name": "Yoga Mat",             "price": 599,  "stock": 100,"category": "Fitness"},
    {"id": 6, "name": "Coffee Mug",           "price": 299,  "stock": 200,"category": "Kitchen"},
]

orders = []

# ---------- Middleware: track every request ----------
@app.before_request
def start_timer():
    request._start_time = time.time()

@app.after_request
def track_metrics(response):
    latency = time.time() - getattr(request, '_start_time', time.time())
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.path,
        status=response.status_code
    ).inc()
    REQUEST_LATENCY.labels(endpoint=request.path).observe(latency)
    return response

# ---------- Routes ----------
@app.route('/')
def home():
    return render_template('index.html', products=PRODUCTS)

@app.route('/products')
def products():
    category = request.args.get('category')
    if category:
        filtered = [p for p in PRODUCTS if p['category'] == category]
    else:
        filtered = PRODUCTS
    return render_template('products.html', products=filtered, categories=get_categories())

@app.route('/api/products')
def api_products():
    return jsonify({"products": PRODUCTS, "count": len(PRODUCTS)})

@app.route('/api/order', methods=['POST'])
def place_order():
    data = request.get_json()
    product_id = data.get('product_id')
    product = next((p for p in PRODUCTS if p['id'] == product_id), None)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    if product['stock'] <= 0:
        return jsonify({"error": "Out of stock"}), 400
    product['stock'] -= 1
    order = {
        "order_id": len(orders) + 1,
        "product": product['name'],
        "price": product['price'],
        "status": "confirmed"
    }
    orders.append(order)
    ORDER_COUNT.inc()
    return jsonify({"message": "Order placed!", "order": order}), 201

@app.route('/api/orders')
def get_orders():
    return jsonify({"orders": orders, "total": len(orders)})

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "ecommerce-app", "version": "1.0"}), 200

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

def get_categories():
    return list(set(p['category'] for p in PRODUCTS))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
