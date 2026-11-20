# --- TEST SUITE FOR INVENTORY MANAGEMENT SYSTEM ---
from unittest.mock import MagicMock, patch
import app as server
import cli
import external_api
import pytest

# --- 1. FLASK REST API TESTS ---
@pytest.fixture
def api_client():
    server.inventory_list.clear()
    server.next_item_id = 1
    server.app.config["TESTING"] = True

    with server.app.test_client() as client:
        yield client


#--test cases for the REST API endpoints ---
def test_create_and_fetch_product(api_client):
    create_res = api_client.post(
        "/inventory",
        json={
            "name": "Fresh Milk 500ml",
            "brand": "Brookside",
            "category": "Dairy",
            "quantity": 30,
            "price": 65.0,
        },
    )
    assert create_res.status_code == 201
    created_item = create_res.get_json()
    assert created_item["id"] == 1
    assert created_item["name"] == "Fresh Milk 500ml"

    get_res = api_client.get("/inventory/1")
    assert get_res.status_code == 200
    assert get_res.get_json()["brand"] == "Brookside"

# test auto-enrichment of product details using external API when creating a new product
@patch("app.get_details_by_barcode")
def test_auto_enrichment_on_create(mock_barcode_api, api_client):
    mock_barcode_api.return_value = {
        "barcode": "5449000000996",
        "name": "Coca-Cola",
        "brand": "Coca-Cola",
        "category": "Beverages",
    }

    res = api_client.post(
        "/inventory",
        json={"barcode": "5449000000996", "quantity": 40, "price": 100.0},
    )
    assert res.status_code == 201
    item = res.get_json()
    assert item["name"] == "Coca-Cola"
    assert item["category"] == "Beverages"
    mock_barcode_api.assert_called_once_with("5449000000996")

# test for editing an existing product in the inventory
def test_edit_product(api_client):
    api_client.post(
        "/inventory",
        json={"name": "White Bread", "quantity": 12, "price": 60.0},
    )

    edit_res = api_client.put(
        "/inventory/1", json={"quantity": 25, "price": 65.0}
    )
    assert edit_res.status_code == 200
    assert edit_res.get_json()["quantity"] == 25
    assert edit_res.get_json()["price"] == 65.0

# test for deleting a product from the inventory
def test_delete_product(api_client):
    api_client.post(
        "/inventory",
        json={"name": "Brown Sugar 1kg", "quantity": 20, "price": 170.0},
    )

    del_res = api_client.delete("/inventory/1")
    assert del_res.status_code == 200

    check_res = api_client.get("/inventory/1")
    assert check_res.status_code == 404


# --- EXTERNAL API MODULE TESTS ---
@patch("external_api.requests.get")
def test_external_barcode_lookup_success(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "status": 1,
        "product": {
            "product_name": "Nutella",
            "brands": "Ferrero",
            "categories": "Spreads",
        },
    }
    mock_get.return_value = mock_response

# test for searching a product in the external catalog by barcode
    result = external_api.get_details_by_barcode("3017620422003")
    assert result["name"] == "Nutella"
    assert result["brand"] == "Ferrero"
    mock_get.assert_called_once()
    called_url = mock_get.call_args.args[0]
    assert "world.openfoodfacts.net" in called_url
    assert "3017620422003" in called_url

# test for searching a product in the external catalog by title
@patch("external_api.requests.get")
def test_external_title_search_not_found(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"products": []}
    mock_get.return_value = mock_response

    result = external_api.find_details_by_title("NonExistentSnackXYZ")
    assert result is None

# --- CLI MODULE TESTS ---
@patch("cli.requests.post")
@patch("builtins.input", side_effect=["5449000000996", "", "15", "120.0"])
def test_cli_add_product_flow(mock_input, mock_post, capsys):
    mock_post.return_value.status_code = 201
    mock_post.return_value.json.return_value = {
        "id": 1,
        "barcode": "5449000000996",
        "name": "Coca-Cola",
        "quantity": 15,
        "price": 120.0,
    }

    cli.handle_add_product()
    captured = capsys.readouterr()

    assert "Product added:" in captured.out
    assert "Coca-Cola" in captured.out
    mock_post.assert_called_once()

# test for showing empty inventory in the CLI
@patch("cli.requests.get")
def test_cli_show_empty_inventory(mock_get, capsys):
    mock_get.return_value.json.return_value = []

    cli.show_inventory()
    captured = capsys.readouterr()

    assert "Inventory is currently empty" in captured.out
