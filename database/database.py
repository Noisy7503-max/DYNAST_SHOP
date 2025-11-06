import aiosqlite
import json
from datetime import datetime
from config import DB_NAME, CATEGORIES

class Database:
    def __init__(self):
        self.db_name = DB_NAME

    async def create_tables(self):
        async with aiosqlite.connect(self.db_name) as db:
            # Users table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    full_name TEXT,
                    city TEXT,
                    phone TEXT,
                    referral_code TEXT UNIQUE,
                    referred_by INTEGER,
                    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_spent REAL DEFAULT 0,
                    has_referral_bonus BOOLEAN DEFAULT FALSE,
                    orders_count INTEGER DEFAULT 0
                )
            ''')

            # Categories table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    is_active BOOLEAN DEFAULT TRUE
                )
            ''')

            # Brands table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS brands (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_id TEXT,
                    name TEXT,
                    description TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (category_id) REFERENCES categories (id)
                )
            ''')

            # Products table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    brand_id INTEGER,
                    name TEXT,
                    description TEXT,
                    price REAL,
                    photo TEXT,
                    is_available BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (brand_id) REFERENCES brands (id)
                )
            ''')

            # Orders table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    products TEXT,
                    total_amount REAL,
                    status TEXT DEFAULT 'pending',
                    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    courier_id INTEGER,
                    delivery_time TEXT,
                    delivery_location TEXT,
                    courier_description TEXT,
                    is_completed BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')

            # Courier complaints table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS complaints (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER,
                    user_id INTEGER,
                    complaint_text TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (order_id) REFERENCES orders (id),
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')

            # Initialize categories
            for category_id, category_name in CATEGORIES.items():
                await db.execute(
                    'INSERT OR IGNORE INTO categories (id, name) VALUES (?, ?)',
                    (category_id, category_name)
                )

            await db.commit()

    # User methods
    async def add_user(self, user_id, username, full_name, city, phone, referral_code=None, referred_by=None):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
                INSERT OR IGNORE INTO users (user_id, username, full_name, city, phone, referral_code, referred_by)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, username, full_name, city, phone, referral_code, referred_by))
            await db.commit()

    async def get_user(self, user_id):
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)) as cursor:
                return await cursor.fetchone()

    async def get_all_users(self):
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute('SELECT * FROM users ORDER BY registration_date DESC') as cursor:
                return await cursor.fetchall()



    async def update_user_spent(self, user_id, amount):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute(
                'UPDATE users SET total_spent = total_spent + ?, orders_count = orders_count + 1 WHERE user_id = ?', 
                (amount, user_id)
            )
            await db.commit()

    async def check_referral_bonus(self, user_id):
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute(
                'SELECT referred_by FROM users WHERE user_id = ? AND referred_by IS NOT NULL', 
                (user_id,)
            ) as cursor:
                result = await cursor.fetchone()
                if result:
                    referrer_id = result[0]
                    async with db.execute(
                        'SELECT total_spent, has_referral_bonus FROM users WHERE user_id = ?', 
                        (referrer_id,)
                    ) as cursor2:
                        referrer_data = await cursor2.fetchone()
                        if referrer_data and referrer_data[0] >= 500 and not referrer_data[1]:
                            await db.execute(
                                'UPDATE users SET has_referral_bonus = TRUE WHERE user_id = ?', 
                                (referrer_id,)
                            )
                            await db.commit()
                            return referrer_id
        return None

    # Category methods
    async def get_categories(self):
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute('SELECT * FROM categories WHERE is_active = TRUE') as cursor:
                return await cursor.fetchall()

    async def get_all_categories(self):
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute('SELECT * FROM categories') as cursor:
                return await cursor.fetchall()

    async def toggle_category(self, category_id, is_active):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('UPDATE categories SET is_active = ? WHERE id = ?', (is_active, category_id))
            await db.commit()

    async def add_category(self, category_id, name):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute(
                'INSERT OR REPLACE INTO categories (id, name) VALUES (?, ?)',
                (category_id, name)
            )
            await db.commit()

    # Brand methods
    async def add_brand(self, category_id, name, description=""):
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute(
                'INSERT INTO brands (category_id, name, description) VALUES (?, ?, ?)', 
                (category_id, name, description)
            )
            await db.commit()
            return cursor.lastrowid

    async def get_brands_by_category(self, category_id):
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute(
                'SELECT * FROM brands WHERE category_id = ? AND is_active = TRUE', 
                (category_id,)
            ) as cursor:
                return await cursor.fetchall()

    async def get_all_brands(self):
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute('''
                SELECT b.*, c.name as category_name 
                FROM brands b 
                JOIN categories c ON b.category_id = c.id
            ''') as cursor:
                return await cursor.fetchall()

    async def get_brand(self, brand_id):
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute('SELECT * FROM brands WHERE id = ?', (brand_id,)) as cursor:
                return await cursor.fetchone()

    async def toggle_brand(self, brand_id, is_active):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('UPDATE brands SET is_active = ? WHERE id = ?', (is_active, brand_id))
            await db.commit()

    async def delete_brand(self, brand_id):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('DELETE FROM brands WHERE id = ?', (brand_id,))
            await db.commit()

    async def update_brand(self, brand_id, name, description):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute(
                'UPDATE brands SET name = ?, description = ? WHERE id = ?',
                (name, description, brand_id)
            )
            await db.commit()

    # Product methods
    async def add_product(self, brand_id, name, description, price, photo):
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('''
                INSERT INTO products (brand_id, name, description, price, photo)
                VALUES (?, ?, ?, ?, ?)
            ''', (brand_id, name, description, price, photo))
            await db.commit()
            return cursor.lastrowid
        
    async def get_products_by_brand(self, brand_id):
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute(
                'SELECT * FROM products WHERE brand_id = ? ORDER BY name',  
                (brand_id,)
            ) as cursor:
                return await cursor.fetchall()

    async def get_all_products(self):
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute('''
                SELECT p.*, b.name as brand_name, c.name as category_name 
                FROM products p 
                JOIN brands b ON p.brand_id = b.id 
                JOIN categories c ON b.category_id = c.id
                ORDER BY p.created_at DESC
            ''') as cursor:
                return await cursor.fetchall()

    async def get_product(self, product_id):
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute('SELECT * FROM products WHERE id = ?', (product_id,)) as cursor:
                return await cursor.fetchone()

    async def toggle_product_availability(self, product_id, is_available):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('UPDATE products SET is_available = ? WHERE id = ?', (is_available, product_id))
            await db.commit()

    async def delete_product(self, product_id):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('DELETE FROM products WHERE id = ?', (product_id,))
            await db.commit()

    async def update_product(self, product_id, name, description, price):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute(
                'UPDATE products SET name = ?, description = ?, price = ? WHERE id = ?',
                (name, description, price, product_id)
            )
            await db.commit()

    # Order methods
    async def create_order(self, user_id, products, total_amount):
        async with aiosqlite.connect(self.db_name) as db:
            # products - это список ID товаров
            products_json = str(products)
            await db.execute('''
                INSERT INTO orders (user_id, products, total_amount)
                VALUES (?, ?, ?)
            ''', (user_id, products_json, total_amount))
            await db.commit()
            
            # Get the last inserted order id
            async with db.execute('SELECT last_insert_rowid()') as cursor:
                order_id = (await cursor.fetchone())[0]
                return order_id


    async def get_pending_orders(self):
        """Получить заказы ожидающие подтверждения"""
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute('''
                SELECT o.*, u.full_name, u.phone, u.city 
                FROM orders o 
                JOIN users u ON o.user_id = u.user_id 
                WHERE o.status = "pending"
                ORDER BY o.order_date DESC
            ''') as cursor:
                orders = await cursor.fetchall()
                return orders

    async def get_all_orders(self):
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute('''
                SELECT o.*, u.full_name, u.phone 
                FROM orders o 
                JOIN users u ON o.user_id = u.user_id 
                ORDER BY o.order_date DESC
            ''') as cursor:
                return await cursor.fetchall()

    async def get_orders_by_courier(self, courier_id):
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute(
                'SELECT * FROM orders WHERE courier_id = ? AND is_completed = FALSE ORDER BY order_date DESC', 
                (courier_id,)
            ) as cursor:
                return await cursor.fetchall()

    async def update_order_delivery(self, order_id, courier_id, delivery_time, delivery_location, courier_description):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
                UPDATE orders SET status = "confirmed", courier_id = ?, delivery_time = ?, 
                delivery_location = ?, courier_description = ? WHERE id = ?
            ''', (courier_id, delivery_time, delivery_location, courier_description, order_id))
            await db.commit()

    async def get_user_orders(self, user_id):
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute(
                'SELECT * FROM orders WHERE user_id = ? ORDER BY order_date DESC', 
                (user_id,)
            ) as cursor:
                return await cursor.fetchall()

    async def complete_order(self, order_id):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('UPDATE orders SET is_completed = TRUE WHERE id = ?', (order_id,))
            await db.commit()

    async def get_order(self, order_id):
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute('SELECT * FROM orders WHERE id = ?', (order_id,)) as cursor:
                return await cursor.fetchone()

    async def update_order_status(self, order_id, status):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('UPDATE orders SET status = ? WHERE id = ?', (status, order_id))
            await db.commit()

    async def assign_courier(self, order_id, courier_id):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('UPDATE orders SET courier_id = ? WHERE id = ?', (courier_id, order_id))
            await db.commit()

    async def add_complaint(self, order_id, user_id, complaint_text):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
                INSERT INTO complaints (order_id, user_id, complaint_text)
                VALUES (?, ?, ?)
            ''', (order_id, user_id, complaint_text))
            await db.commit()

    # Admin statistics
    async def get_admin_stats(self):
        async with aiosqlite.connect(self.db_name) as db:
            # Total users
            async with db.execute('SELECT COUNT(*) FROM users') as cursor:
                total_users = (await cursor.fetchone())[0]

            # Total orders
            async with db.execute('SELECT COUNT(*) FROM orders') as cursor:
                total_orders = (await cursor.fetchone())[0]

            # Total revenue
            async with db.execute('SELECT SUM(total_amount) FROM orders WHERE is_completed = TRUE') as cursor:
                total_revenue = (await cursor.fetchone())[0] or 0

            # Pending orders
            async with db.execute('SELECT COUNT(*) FROM orders WHERE status = "pending"') as cursor:
                pending_orders = (await cursor.fetchone())[0]

            # Today's orders
            async with db.execute('SELECT COUNT(*) FROM orders WHERE DATE(order_date) = DATE("now")') as cursor:
                today_orders = (await cursor.fetchone())[0]

            return {
                'total_users': total_users,
                'total_orders': total_orders,
                'total_revenue': total_revenue,
                'pending_orders': pending_orders,
                'today_orders': today_orders
            }

db = Database()