from bot.db_connect import get_connection

def register_user(telegram_id, username):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM users WHERE telegram_id=%s", (telegram_id,))
    exists = cur.fetchone()

    if not exists:
        cur.execute(
            "INSERT INTO users (telegram_id, username) VALUES (%s, %s)",
            (telegram_id, username)
        )
        conn.commit()

    cur.close()
    conn.close()


def get_products_by_category(category_id):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM products WHERE category_id=%s", (category_id,))
    items = cur.fetchall()

    cur.close()
    conn.close()
    return items


def add_favorite(user_id, product_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM favorites WHERE user_id=%s AND product_id=%s",
        (user_id, product_id)
    )
    exists = cur.fetchone()

    if not exists:
        cur.execute(
            "INSERT INTO favorites (user_id, product_id) VALUES (%s, %s)",
            (user_id, product_id)
        )
        conn.commit()

    cur.close()
    conn.close()
