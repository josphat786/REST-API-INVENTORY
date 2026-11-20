# Storefront Admin Inventory Management System

A Python-based inventory management REST API and command-line administrator portal built with **Flask** and **Requests**. It enables retail employees to add, view, edit, and delete inventory items while automatically supplementing product metadata (name, brand, and category) in real time from the **OpenFoodFacts API**.

---

## Features

* **Flask REST API (`app.py`):** Full CRUD endpoints (`/inventory`) with JSON responses, proper HTTP status codes (`200`, `201`, `400`, `404`, `409`), and duplicate barcode validation.
* **Real-Time Product Enrichment (`external_api.py`):** Automatically fetches missing product details by barcode or product title from `https://openfoodfacts.net`.
* **Interactive CLI Admin Portal (`cli.py`):** Menu-driven command-line interface for viewing stock, registering new items, updating records, deleting items, and searching the external catalog.
* **Automated Unit Tests (`test_app.py`):** Comprehensive `pytest` suite using `unittest.mock` to validate REST API routes, external HTTP requests, and CLI user interactions offline.

---

## Project Structure

```text
REST API INVENTORY/
├── app.py              # Flask REST API server and in-memory inventory store
├── external_api.py     # OpenFoodFacts API client (barcode & title lookups)
├── cli.py              # Interactive command-line interface for administrators
├── test_app.py         # Unit tests for API, external lookups, and CLI
├── requirements.txt    # Pinned Python dependencies
└── README.md           # Project documentation and license
```

---

## Setup & Installation

### 1. Create and Activate a Virtual Environment

**Windows (PowerShell):**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

*(Note: If PowerShell blocks script execution, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` once, then re-run `.\venv\Scripts\Activate.ps1`.)*

**macOS / Linux (Bash/Zsh):**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Running the Application

Because the CLI communicates with the Flask REST API over HTTP, run them in **two separate terminals** (with the virtual environment activated in both).

### Terminal 1: Start the Flask REST API Server

```bash
python app.py
```

The API server starts at `http://127.0.0.1:5000`. Keep this terminal running while using the CLI.

### Terminal 2: Launch the CLI Admin Portal

```bash
python cli.py
```

#### Available CLI Menu Options

1. **View All Products** — Displays all inventory records in a formatted table.
2. **Add New Product** — Registers a new item; entering a valid barcode auto-fetches missing product details from OpenFoodFacts.
3. **Edit Existing Product** — Updates an item's name, stock quantity, or unit price by its numeric ID.
4. **Delete Product** — Removes an item from inventory by its numeric ID.
5. **Search External Product Catalog** — Queries `https://openfoodfacts.net` directly by barcode or product name.
6. **Exit** — Closes the CLI portal.

---

## REST API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **`GET`** | `/inventory` | Retrieve all products currently in inventory. |
| **`GET`** | `/inventory/<int:item_id>` | Retrieve a single product by its numeric ID. |
| **`POST`** | `/inventory` | Add a new product (auto-fills missing fields via OpenFoodFacts if `barcode` or `name` is provided). |
| **`PUT` / `PATCH`** | `/inventory/<int:item_id>` | Update an existing product's name, brand, category, quantity, or price. |
| **`DELETE`** | `/inventory/<int:item_id>` | Remove a product from inventory by ID. |
| **`GET`** | `/inventory/lookup` | Search OpenFoodFacts directly using `?barcode=<code>` or `?name=<title>`. |

### Example `POST /inventory` Request

```json
{
  "barcode": "3017620422003",
  "quantity": 100,
  "price": 650.00
}
```

### Example `201 Created` Response

```json
{
  "id": 1,
  "barcode": "3017620422003",
  "name": "Nutella",
  "brand": "Nutella",
  "category": "Pâtes à tartiner aux noisettes et au cacao, en:Pâtes à tartiner",
  "quantity": 100,
  "price": 650.0
}
```

---

## Running Unit Tests

Run the full `pytest` suite with verbose output:

```bash
pytest -v
```

External HTTP requests to `https://openfoodfacts.net` and CLI user prompts are mocked so all 8 unit tests execute rapidly and reliably offline.

---

## Technical Notes

* **In-Memory Storage:** Inventory items are stored in memory (`inventory_list` in `app.py`). Restarting the Flask server resets the inventory to an empty list.
* **External API:** Product lookups target the OpenFoodFacts staging environment (`https://openfoodfacts.net`).

---

## License

MIT License

Copyright (c) 2026 Josphat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
