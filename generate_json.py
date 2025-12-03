import json
from bot.db_connect import get_connection

OUTPUT_PATH = "cart/products.json"

def generate_products_json():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT id, name, price FROM products")
    rows = cur.fetchall()

    data = {}

    for p in rows:
        data[p["id"]] = {
            "name": p["name"],
            "price": float(p["price"])
        }

    cur.close()
    conn.close()

    # Save as JSON
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print("✅ products.json updated!")

if __name__ == "__main__":
    generate_products_json()
