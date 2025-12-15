Інструкція з розгортання
# 1. Вимоги до середовища

- Python 3.10+
- MySQL Server 8.0+
- Git (за потреби)
- Telegram (Desktop або мобільний)

Рекомендовано: VS Code / PyCharm, MySQL Workbench.

# 2. Отримання коду

### Варіант A: клонування репозиторію
```bash
git clone https://github.com/isdanchuk/Kolosky_Bot.git
cd Kolosky_Bot
Варіант B: архів
Розпакуй архів у папку та відкрий її в IDE.

3. Підготовка Python-середовища
Windows (PowerShell)
bash
Копіювати код
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
Якщо requirements.txt відсутній, мінімальний набір:

bash
Копіювати код
pip install aiogram python-dotenv mysql-connector-python pandas openpyxl
4. Налаштування конфігурації (.env)
Створи файл .env у корені проєкту та заповни:

env
Копіювати код
BOT_TOKEN=ваш_токен_бота
DB_HOST=localhost
DB_USER=ваш_користувач
DB_PASSWORD=ваш_пароль
DB_NAME=назва_бази
Важливо: .env не публікується. Не додавай токени/паролі в GitHub.

5. Підключення до наявної бази даних MySQL
У проєкті використовується вже реалізована схема БД (таблиці каталогу та стану користувача: users, products, categories, subcategories, favorites, cart_items, product_images).

Варіант A (рекомендовано): імпорт дампу .sql
Якщо у вас є db_dump.sql:

bash
Копіювати код
mysql -u root -p < db_dump.sql
Або імпорт через MySQL Workbench (Data Import).

Варіант B: БД вже існує локально
Переконайся, що MySQL запущений і параметри в .env правильні.

6. Оновлення каталогу (Excel → БД → JSON)
6.1 Оновити Excel
Файл каталогу: data/products.xlsx
Внеси зміни і збережи.

6.2 Синхронізувати Excel → MySQL
bash
Копіювати код
python update_products.py
6.3 Згенерувати JSON для веб-кошика (за потреби)
bash
Копіювати код
python generate_json.py
Файл результату: cart/products.json

7. Запуск Telegram-бота
bash
Копіювати код
python main.py
Після запуску бот переходить у режим обробки оновлень (polling) і готовий приймати команди в Telegram.

8. Використання бота
Напиши боту /start

Перевір основні сценарії:

Каталог → категорія → товар

Додати в кошик → Кошик → сума

Вибране

Оформлення (Telegram/Direct/посилання на веб-кошик)

9. Веб-сторінка кошика (cart)
Локально
Відкрий cart/index.html у браузері (подвійний клік)
Переконайся, що cart/products.json актуальний.

GitHub Pages (якщо налаштовано)
Сторінку можна опублікувати як статичний сайт через GitHub Pages.

10. Типові проблеми
1) ModuleNotFoundError / бот не запускається
Активуй .venv і встанови залежності (pip install -r requirements.txt).

2) Помилка підключення до MySQL
Перевір .env і статус MySQL. За потреби імпортуй дамп БД.

3) Каталог не оновився після Excel
Запусти python update_products.py.

4) JSON неактуальний для cart/
Запусти python generate_json.py.
