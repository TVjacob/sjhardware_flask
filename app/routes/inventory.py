from flask import Blueprint, request, jsonify
from app import db
from app.models import Product, Category
from datetime import datetime

inventory_bp = Blueprint('inventory', __name__, url_prefix='/inventory')

# --- Add a product (quantity cannot be set manually) ---
@inventory_bp.route('/products', methods=['POST'])
def add_product():
    data = request.json
    product = Product(
        name=data['name'],
        sku=data['sku'],
        category_id=data.get('category_id'),
        quantity=0,  # always start at 0
        price=data.get('price', 0),
        status=1,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.session.add(product)
    db.session.commit()
    return jsonify({"message": "Product added", "product_id": product.id}), 201

# --- View all products ---
@inventory_bp.route('/products', methods=['GET'])
def list_products():
    products = Product.query.all()
    result = []
    for p in products:
        result.append({
            "id": p.id,
            "name": p.name,
            "sku": p.sku,
            "category_id": p.category_id,
            "quantity": p.quantity,
            "price": p.price,
            "status": p.status,
            "created_at": p.created_at,
            "updated_at": p.updated_at
        })
    return jsonify(result)


# --- Find product by ID ---
@inventory_bp.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    p = Product.query.get_or_404(id)
    return jsonify({
        "id": p.id,
        "name": p.name,
        "sku": p.sku,
        "category_id": p.category_id,
        "quantity": p.quantity,
        "price": p.price,
        "status": p.status,
        "created_at": p.created_at,
        "updated_at": p.updated_at
    })

# --- Find product by SKU or Name ---
@inventory_bp.route('/products/search', methods=['GET'])
def search_product():
    sku = request.args.get('sku')
    name = request.args.get('name')
    query = Product.query
    if sku:
        query = query.filter_by(sku=sku)
    if name:
        query = query.filter(Product.name.ilike(f"%{name}%"))
    products = query.all()
    result = []
    for p in products:
        result.append({
            "id": p.id,
            "name": p.name,
            "sku": p.sku,
            "category_id": p.category_id,
            "quantity": p.quantity,
            "price": p.price,
            "status": p.status,
            "created_at": p.created_at,
            "updated_at": p.updated_at
        })
    return jsonify(result)

# --- Update product (quantity cannot be manually updated here) ---
@inventory_bp.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    product = Product.query.get_or_404(id)
    data = request.json
    product.name = data.get('name', product.name)
    product.sku = data.get('sku', product.sku)
    product.category_id = data.get('category_id', product.category_id)
    # product.quantity = data.get('quantity', product.quantity)  # removed
    product.price = data.get('price', product.price)
    product.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({"message": "Product updated", "product_id": product.id})

# --- Delete product ---
@inventory_bp.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted", "product_id": id})


# ---------------- Category CRUD ---------------- #

# --- Add category ---
@inventory_bp.route('/categories', methods=['POST'])
def add_category():
    data = request.json
    category = Category(
        name=data['name'],
        description=data.get('description'),
        status=1,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.session.add(category)
    db.session.commit()
    return jsonify({"message": "Category added", "category_id": category.id}), 201

# --- View all categories ---
@inventory_bp.route('/categories', methods=['GET'])
def list_categories():
    categories = Category.query.all()
    result = [{"id": c.id, "name": c.name, "description": c.description,
               "status": c.status, "created_at": c.created_at, "updated_at": c.updated_at} 
              for c in categories]
    return jsonify(result)

# --- Find category by ID ---
@inventory_bp.route('/categories/<int:id>', methods=['GET'])
def get_category(id):
    c = Category.query.get_or_404(id)
    return jsonify({
        "id": c.id,
        "name": c.name,
        "description": c.description,
        "status": c.status,
        "created_at": c.created_at,
        "updated_at": c.updated_at
    })

# --- Update category ---
@inventory_bp.route('/categories/<int:id>', methods=['PUT'])
def update_category(id):
    c = Category.query.get_or_404(id)
    data = request.json
    c.name = data.get('name', c.name)
    c.description = data.get('description', c.description)
    c.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({"message": "Category updated", "category_id": c.id})

# --- Delete category ---
@inventory_bp.route('/categories/<int:id>', methods=['DELETE'])
def delete_category(id):
    c = Category.query.get_or_404(id)
    db.session.delete(c)
    db.session.commit()
    return jsonify({"message": "Category deleted", "category_id": id})
