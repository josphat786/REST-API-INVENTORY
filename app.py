from external_api import find_details_by_title, get_details_by_barcode
from flask import Flask, jsonify, request

app = Flask(__name__)

# In-memory inventory storage
inventory_list = []
next_item_id = 1

# Search for a product in the inventory by its ID
def find_stock_by_id(item_id):
    return next(
        (product for product in inventory_list if product["id"] == item_id),
        None,
    )

# Flask route to get all products in the inventory
@app.route("/inventory", methods=["GET"])
def get_all_products():
    return jsonify(inventory_list), 200

# Flask route to get a specific product by its ID
@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_product_by_id(item_id):
    product = find_stock_by_id(item_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product), 200

# Flask route to register a new product in the inventory
@app.route("/inventory", methods=["POST"])
def register_product():
    global next_item_id
    incoming_data = request.get_json() or {}
    barcode = incoming_data.get("barcode")
    name = incoming_data.get("name")
    brand = incoming_data.get("brand")
    category = incoming_data.get("category")

    if barcode and any(item["barcode"] == barcode for item in inventory_list):
        return (
            jsonify({"error": "A product with this barcode already exists"}),
            409,
        )

    catalog_info = None
    if barcode and (not name or not brand or not category):
        catalog_info = get_details_by_barcode(barcode)
    elif name and (not brand or not category):
        catalog_info = find_details_by_title(name)

    if catalog_info:
        name = name or catalog_info.get("name")
        barcode = barcode or catalog_info.get("barcode")
        brand = brand or catalog_info.get("brand")
        category = category or catalog_info.get("category")

    if not name:
        return (
            jsonify({"error": "Product name or a valid barcode is required"}),
            400,
        )

    new_product = {
        "id": next_item_id,
        "barcode": barcode,
        "name": name,
        "brand": brand,
        "category": category,
        "quantity": incoming_data.get("quantity", 0),
        "price": incoming_data.get("price", 0.0),
    }
    inventory_list.append(new_product)
    next_item_id += 1

    return jsonify(new_product), 201


@app.route("/inventory/<int:item_id>", methods=["PUT", "PATCH"])
def edit_product(item_id):
    product = find_stock_by_id(item_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    incoming_data = request.get_json() or {}
    product["name"] = incoming_data.get("name", product["name"])
    product["brand"] = incoming_data.get("brand", product["brand"])
    product["category"] = incoming_data.get("category", product["category"])
    product["quantity"] = incoming_data.get("quantity", product["quantity"])
    product["price"] = incoming_data.get("price", product["price"])

    return jsonify(product), 200


@app.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_product(item_id):
    product = find_stock_by_id(item_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    inventory_list.remove(product)
    return jsonify({"message": f"Product {item_id} deleted"}), 200

# Search for a product in the external catalog
@app.route("/inventory/lookup", methods=["GET"])
def search_external_product():
    barcode = request.args.get("barcode")
    name = request.args.get("name")

    if barcode:
        result = get_details_by_barcode(barcode)
    elif name:
        result = find_details_by_title(name)
    else:
        return jsonify({"error": "Provide 'barcode' or 'name' parameter"}), 400

    if not result:
        return jsonify({"error": "Product not found in external catalog"}), 404
    return jsonify(result), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
