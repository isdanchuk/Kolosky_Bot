import pandas as pd
from bot.db_connect import get_connection


EXCEL_PATH = "data/products.xlsx"


def sync_products_from_excel():
    # 1. Читаємо Excel у DataFrame
    df = pd.read_excel(EXCEL_PATH)

    # Перевіряємо, що всі обов'язкові колонки є
    required_cols = {"id", "category_id", "name", "description", "price", "main_image", "product_url"}
    if not required_cols.issubset(df.columns):
        missing = required_cols - set(df.columns)
        raise ValueError(f"В Excel не вистачає колонок: {', '.join(missing)}")

    conn = get_connection()
    cur = conn.cursor()

    # Множина id, які є в Excel
    excel_ids = set()

    for _, row in df.iterrows():
        prod_id = int(row["id"])
        excel_ids.add(prod_id)

        category_id = int(row["category_id"])
        name = str(row["name"])
        description = "" if pd.isna(row["description"]) else str(row["description"])
        price = float(row["price"])
        main_image = str(row["main_image"])
        product_url = "" if pd.isna(row["product_url"]) else str(row["product_url"])

        # Вставка/оновлення запису
        cur.execute("""
            INSERT INTO products (id, category_id, name, description, price, main_image, product_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                category_id = VALUES(category_id),
                name        = VALUES(name),
                description = VALUES(description),
                price       = VALUES(price),
                main_image  = VALUES(main_image),
                product_url = VALUES(product_url)
        """, (prod_id, category_id, name, description, price, main_image, product_url))

    # Видалити товари, яких немає в Excel
    if excel_ids:
        placeholders = ",".join(["%s"] * len(excel_ids))
        cur.execute(f"DELETE FROM products WHERE id NOT IN ({placeholders})", tuple(excel_ids))
    else:
        cur.execute("DELETE FROM products")

    conn.commit()
    cur.close()
    conn.close()

    print("✅ База даних синхронізована з Excel")


if __name__ == "__main__":
    sync_products_from_excel()
