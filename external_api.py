import requests

OFF_BASE_URL = "https://world.openfoodfacts.net"
CUSTOM_HEADERS = {"User-Agent": "StorefrontInventoryPortal/1.0"}

## --- EXTERNAL API MODULE ---
def get_details_by_barcode(code):
    endpoint = f"{OFF_BASE_URL}/api/v2/product/{code}.json"
    try:
        # Fetch product details from OpenFoodFacts API using the barcode
        res = requests.get(endpoint, headers=CUSTOM_HEADERS, timeout=5)
        res.raise_for_status()
        response_data = res.json()
        if response_data.get("status") == 1:
            info = response_data.get("product", {})
            return {
                "barcode": code,
                "name": info.get("product_name", "Unnamed Item"),
                "brand": info.get("brands", "Generic"),
                "category": info.get("categories", "General"),
            }
    except requests.RequestException:
        return None
    return None

### --- EXTERNAL API MODULE ---
def find_details_by_title(title):
    endpoint = f"{OFF_BASE_URL}/cgi/search.pl"
    query_params = {
        "search_terms": title,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": 1,
    }
    try:
        res = requests.get(
            endpoint, params=query_params, headers=CUSTOM_HEADERS, timeout=5
        )
        res.raise_for_status()
        response_data = res.json()
        matches = response_data.get("products", [])
        if matches:
            top_match = matches[0]
            return {
                "barcode": top_match.get("code"),
                "name": top_match.get("product_name", title),
                "brand": top_match.get("brands", "Generic"),
                "category": top_match.get("categories", "General"),
            }
    except requests.RequestException:
        return None
    return None
