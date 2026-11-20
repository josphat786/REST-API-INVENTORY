import requests

SERVER_URL = "http://127.0.0.1:5000"

# Display all products in the inventory
def show_inventory():
    response = requests.get(f"{SERVER_URL}/inventory")
    products = response.json()
    if not products:
        print("\n[Inventory is currently empty]")
        return
# Display product details in a formatted table
    print(
        f"\n{'ID':<4} | {'Barcode':<14} | {'Product Name':<25} | {'Brand':<15} | {'Qty':<5} | {'Price':<8}"
    )
    print("-" * 82)
    for item in products:
        print(
            f"{item['id']:<4} | {str(item['barcode'] or 'N/A'):<14} | "
            f"{item['name'][:25]:<25} | {str(item['brand'] or 'N/A')[:15]:<15} | "
            f"{item['quantity']:<5} | {item['price']:<8.2f}"
        )

# Handle adding a new product to the inventory
def handle_add_product():
    print("\n--- Add New Product ---")
    barcode = (
        input("Barcode (optional - auto-fetches details): ").strip() or None
    )
    name = input("Product Name (optional if barcode given): ").strip() or None
    quantity = int(input("Stock Quantity: ") or 0)
    price = float(input("Unit Price: ") or 0.0)

    request_body = {
        "barcode": barcode,
        "name": name,
        "quantity": quantity,
        "price": price,
    }
    response = requests.post(f"{SERVER_URL}/inventory", json=request_body)
    if response.status_code == 201:
        print("Product added:", response.json())
    else:
        print("Error:", response.json().get("error"))

# Handle editing an existing product in the inventory
def handle_edit_product():
    item_id = input("\nEnter numeric Product ID to edit (e.g., 1): ").strip()
    if not item_id.isdigit():
        print("Error: Product ID must be a number.")
        return

    print("Leave blank to keep current values:")
    name = input("New Product Name: ").strip()
    quantity = input("New Stock Quantity: ").strip()
    price = input("New Unit Price: ").strip()

    changes = {}
    if name:
        changes["name"] = name
    if quantity:
        changes["quantity"] = int(quantity)
    if price:
        changes["price"] = float(price)

    response = requests.put(f"{SERVER_URL}/inventory/{item_id}", json=changes)
    if response.status_code == 200:
        print("Product updated:", response.json())
    else:
        err = (
            response.json().get("error")
            if response.headers.get("Content-Type") == "application/json"
            else f"HTTP {response.status_code}"
        )
        print("Error:", err)

# Handle deleting a product from the inventory
def handle_delete_product():
    item_id = input("\nEnter numeric Product ID to delete (e.g., 1): ").strip()
    if not item_id.isdigit():
        print("Error: Product ID must be a number.")
        return

    response = requests.delete(f"{SERVER_URL}/inventory/{item_id}")
    if response.headers.get("Content-Type") == "application/json":
        print(response.json().get("message") or response.json().get("error"))
    else:
        print(f"Error: HTTP {response.status_code}")

# Handle searching for a product in the external catalog
def handle_catalog_lookup():
    search_input = input(
        "\nEnter barcode or product name to search OpenFoodFacts: "
    ).strip()
    query = (
        {"barcode": search_input}
        if search_input.isdigit()
        else {"name": search_input}
    )
    response = requests.get(f"{SERVER_URL}/inventory/lookup", params=query)
    if response.status_code == 200:
        print("Product found:", response.json())
    else:
        print("Error:", response.json().get("error"))

# Main CLI loop to interact with the inventory system
def start_cli():
    while True:
        print("\n=== Storefront Admin Inventory CLI ===")
        print("1. View All Products")
        print("2. Add New Product")
        print("3. Edit Existing Product")
        print("4. Delete Product")
        print("5. Search External Product Catalog")
        print("6. Exit")

        choice = input("Select an option (1-6): ").strip()
        try:
            if choice == "1":
                show_inventory()
            elif choice == "2":
                handle_add_product()
            elif choice == "3":
                handle_edit_product()
            elif choice == "4":
                handle_delete_product()
            elif choice == "5":
                handle_catalog_lookup()
            elif choice == "6":
                print("Exiting admin portal.")
                break
            else:
                print("Invalid option. Please choose 1-6.")
        except requests.exceptions.ConnectionError:
            print(
                "\n[Connection Error] Unable to reach the server. Ensure app.py is running."
            )


if __name__ == "__main__":
    start_cli()
