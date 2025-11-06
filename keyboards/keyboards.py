from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import CITIES, CATEGORIES

class Keyboards:
    # Главное меню
    @staticmethod
    def main_menu(user_id, is_admin=False, is_courier=False, has_cart_items=False):
        builder = InlineKeyboardBuilder()
        
        if is_admin:
            builder.add(InlineKeyboardButton(text="👑 АДМИН ПАНЕЛЬ", callback_data="admin_panel"))
        elif is_courier:
            builder.add(InlineKeyboardButton(text="🚗 ПАНЕЛЬ КУРЬЕРА", callback_data="courier_panel"))
        
        builder.add(
            InlineKeyboardButton(text="🛍️ КАТАЛОГ", callback_data="catalog"),
            InlineKeyboardButton(text="🛒 КОРЗИНА", callback_data="view_cart"),
            InlineKeyboardButton(text="👤 ЛИЧНЫЙ КАБИНЕТ", callback_data="personal_cabinet"),
            InlineKeyboardButton(text="🏢 О НАС", callback_data="about"),
            InlineKeyboardButton(text="💬 ТЕХ ПОДДЕРЖКА", callback_data="support"),
            InlineKeyboardButton(text="📞 КОНТАКТЫ", callback_data="contacts")
        )
        builder.adjust(1)
        return builder.as_markup()

    # Клавиатура выбора города
    @staticmethod
    def cities_keyboard():
        builder = InlineKeyboardBuilder()
        for city in CITIES:
            builder.add(InlineKeyboardButton(text=city, callback_data=f"city_{city}"))
        builder.adjust(2)
        return builder.as_markup()

    # Запрос телефона
    @staticmethod
    def request_phone():
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(text="📱 Отправить телефон", callback_data="send_phone"))
        return builder.as_markup()

    # Каталог - категории
    @staticmethod
    def catalog_categories():
        builder = InlineKeyboardBuilder()
        for category_id, category_name in CATEGORIES.items():
            builder.add(InlineKeyboardButton(
                text=category_name, 
                callback_data=f"category_{category_id}"
            ))
        builder.add(InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu"))
        builder.adjust(1)
        return builder.as_markup()

    # Бренды по категории
    @staticmethod
    def brands_menu(brands, category_id):
        builder = InlineKeyboardBuilder()
        for brand in brands:
            builder.add(InlineKeyboardButton(
                text=brand[2], 
                callback_data=f"brand_{brand[0]}"
            ))
        builder.add(InlineKeyboardButton(text="🔙 Назад", callback_data="catalog"))
        builder.adjust(2)
        return builder.as_markup()

    # Товары с навигацией
    @staticmethod
    def products_menu(products, brand_id, current_index=0, in_cart=False, is_available=True):
        builder = InlineKeyboardBuilder()
        
        if products:
            # Навигация
            nav_buttons = []
            if current_index > 0:
                nav_buttons.append(InlineKeyboardButton(
                    text="◀️", 
                    callback_data=f"product_{brand_id}_{current_index-1}"
                ))
            
            nav_buttons.append(InlineKeyboardButton(
                text=f"{current_index + 1}/{len(products)}", 
                callback_data="none"
            ))
            
            if current_index < len(products) - 1:
                nav_buttons.append(InlineKeyboardButton(
                    text="▶️", 
                    callback_data=f"product_{brand_id}_{current_index+1}"
                ))
            
            builder.row(*nav_buttons)
            
            # Кнопки действий (только если товар в наличии)
            if is_available:
                action_buttons = []
                if not in_cart:
                    action_buttons.append(InlineKeyboardButton(
                        text="🛒 В корзину", 
                        callback_data=f"add_to_cart_{products[current_index][0]}"
                    ))
                else:
                    action_buttons.append(InlineKeyboardButton(
                        text="✅ В корзине", 
                        callback_data="already_in_cart"
                    ))
                
                action_buttons.append(InlineKeyboardButton(
                    text="📦 Заказать", 
                    callback_data=f"quick_order_{products[current_index][0]}"
                ))
                
                builder.row(*action_buttons)
            else:
                # Если товара нет в наличии
                builder.row(InlineKeyboardButton(
                    text="❌ Нет в наличии", 
                    callback_data="not_available"
                ))
        
        builder.row(InlineKeyboardButton(text="🔙 К брендам", callback_data=f"category_{products[0][1] if products else ''}"))
        builder.row(InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu"))
        
        return builder.as_markup()

    # Корзина
    @staticmethod
    def cart_keyboard(cart_items):
        builder = InlineKeyboardBuilder()
        if cart_items:
            builder.add(InlineKeyboardButton(text="📦 Оформить заказ", callback_data="checkout"))
            builder.add(InlineKeyboardButton(text="🗑️ Очистить корзину", callback_data="clear_cart"))
        builder.add(InlineKeyboardButton(text="🛍️ Продолжить покупки", callback_data="catalog"))
        builder.add(InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu"))
        builder.adjust(1)
        return builder.as_markup()

    # Личный кабинет
    @staticmethod
    def personal_cabinet():
        builder = InlineKeyboardBuilder()
        builder.add(
            InlineKeyboardButton(text="📦 История заказов", callback_data="order_history"),
            InlineKeyboardButton(text="🎁 Реферальная система", callback_data="referral"),
            InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")
        )
        builder.adjust(1)
        return builder.as_markup()

    # О нас и контакты
    @staticmethod
    def about_and_contacts():
        builder = InlineKeyboardBuilder()
        builder.add(
            InlineKeyboardButton(text="💬 Написать менеджеру", url="https://t.me/dynastsh0p"),
            InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")
        )
        builder.adjust(1)
        return builder.as_markup()

    # Админ панель - главное меню
    @staticmethod
    def admin_panel():
        builder = InlineKeyboardBuilder()
        builder.add(
            InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats"),
            InlineKeyboardButton(text="📦 Заказы", callback_data="admin_orders"),
            InlineKeyboardButton(text="🏷️ Бренды", callback_data="admin_brands"),
            InlineKeyboardButton(text="📦 Товары", callback_data="admin_products"),
            InlineKeyboardButton(text="👤 Пользователи", callback_data="admin_users"),
            InlineKeyboardButton(text="📁 Категории", callback_data="admin_categories"),
            InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
        )
        builder.adjust(2)
        return builder.as_markup()

    # Админ - статистика
    @staticmethod
    def admin_stats():
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(text="🔙 Назад", callback_data="admin_panel"))
        return builder.as_markup()

    # Админ - управление заказами
    @staticmethod
    def admin_orders_menu():
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(text="📋 Список заказов", callback_data="admin_orders_list"))
        builder.add(InlineKeyboardButton(text="🔄 Обновить", callback_data="admin_orders"))
        builder.add(InlineKeyboardButton(text="🔙 Назад", callback_data="admin_panel"))
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def admin_orders_list(orders, current_index=0, user_id=None, username=None):
        builder = InlineKeyboardBuilder()
        
        if orders:
            # Навигация по заказам
            nav_buttons = []
            if current_index > 0:
                nav_buttons.append(InlineKeyboardButton(
                    text="◀️", 
                    callback_data=f"admin_order_{current_index-1}"
                ))
            
            nav_buttons.append(InlineKeyboardButton(
                text=f"{current_index + 1}/{len(orders)}", 
                callback_data="none"
            ))
            
            if current_index < len(orders) - 1:
                nav_buttons.append(InlineKeyboardButton(
                    text="▶️", 
                    callback_data=f"admin_order_{current_index+1}"
                ))
            
            builder.row(*nav_buttons)
            
            # Кнопка "Написать заказчику"
            if username and username != "Не указан" and username != "отсутствует":
                builder.row(InlineKeyboardButton(
                    text="💬 Написать заказчику", 
                    url=f"https://t.me/{username.replace('@', '')}"
                ))
            else:
                builder.row(InlineKeyboardButton(
                    text="📞 Связаться (нет username)", 
                    callback_data="no_username"
                ))
        
        builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="admin_orders"))
        return builder.as_markup()

    # Админ - управление брендами (главное меню)
    @staticmethod
    def admin_brands_menu():
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(text="➕ Добавить бренд", callback_data="add_brand"))
        builder.add(InlineKeyboardButton(text="📋 Список брендов", callback_data="admin_brands_list"))
        builder.add(InlineKeyboardButton(text="🔙 Назад", callback_data="admin_panel"))
        builder.adjust(1)
        return builder.as_markup()

    # Админ - список брендов с навигацией (уникальная клавиатура)
    @staticmethod
    def admin_brands_list_navigation(brands, current_index=0):
        builder = InlineKeyboardBuilder()
        
        if brands:
            # Навигация
            nav_buttons = []
            if current_index > 0:
                nav_buttons.append(InlineKeyboardButton(
                    text="◀️", 
                    callback_data=f"admin_brand_{current_index-1}"
                ))
            
            nav_buttons.append(InlineKeyboardButton(
                text=f"{current_index + 1}/{len(brands)}", 
                callback_data="none"
            ))
            
            if current_index < len(brands) - 1:
                nav_buttons.append(InlineKeyboardButton(
                    text="▶️", 
                    callback_data=f"admin_brand_{current_index+1}"
                ))
            
            builder.row(*nav_buttons)
            
            # Кнопки управления
            brand = brands[current_index]
            status_text = "❌ Скрыть" if brand[4] else "✅ Активировать"
            status_data = f"toggle_brand_{brand[0]}"
            
            builder.row(
                InlineKeyboardButton(text=status_text, callback_data=status_data),
                InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"edit_brand_{brand[0]}")
            )
            builder.row(
                InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"delete_brand_{brand[0]}"),
                InlineKeyboardButton(text="📦 Товары", callback_data=f"brand_products_{brand[0]}")
            )
        
        builder.row(InlineKeyboardButton(text="➕ Добавить бренд", callback_data="add_brand"))
        builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="admin_brands"))
        return builder.as_markup()

    # Админ - управление пользователями (главное меню)
    @staticmethod
    def admin_users_menu():
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(text="📋 Список пользователей", callback_data="admin_users_list"))
        builder.add(InlineKeyboardButton(text="🔙 Назад", callback_data="admin_panel"))
        builder.adjust(1)
        return builder.as_markup()

    # Админ - список пользователей с навигацией (уникальная клавиатура)
    @staticmethod
    def admin_users_list_navigation(users, current_index=0):
        builder = InlineKeyboardBuilder()
        
        if users:
            # Навигация
            nav_buttons = []
            if current_index > 0:
                nav_buttons.append(InlineKeyboardButton(
                    text="◀️", 
                    callback_data=f"admin_user_{current_index-1}"
                ))
            
            nav_buttons.append(InlineKeyboardButton(
                text=f"{current_index + 1}/{len(users)}", 
                callback_data="none"
            ))
            
            if current_index < len(users) - 1:
                nav_buttons.append(InlineKeyboardButton(
                    text="▶️", 
                    callback_data=f"admin_user_{current_index+1}"
                ))
            
            builder.row(*nav_buttons)
            
            # Кнопки управления
            user = users[current_index]
            username = user[1] or "отсутствует"
            
            if username != "отсутствует":
                builder.row(InlineKeyboardButton(
                    text="💬 Написать пользователю", 
                    url=f"https://t.me/{username}"
                ))
            else:
                builder.row(InlineKeyboardButton(
                    text="📞 Нет username", 
                    callback_data="no_user_username"
                ))
            
            builder.row(InlineKeyboardButton(
                text="📊 Статистика", 
                callback_data=f"user_stats_{user[0]}"
            ))
        
        builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="admin_users"))
        return builder.as_markup()

    # Админ - выбор категории для бренда (уникальная клавиатура)
    @staticmethod
    def admin_category_selection():
        builder = InlineKeyboardBuilder()
        for category_id, category_name in CATEGORIES.items():
            builder.add(InlineKeyboardButton(
                text=category_name, 
                callback_data=f"admin_category_{category_id}"
            ))
        builder.add(InlineKeyboardButton(text="❌ Отмена", callback_data="admin_brands"))
        builder.adjust(1)
        return builder.as_markup()
    
    # Админ - товары бренда
    @staticmethod
    def admin_brand_products(brand_id, products):
        builder = InlineKeyboardBuilder()
        
        if products:
            products_text = ""
            for product in products:
                status = "✅" if product[6] else "❌"
                products_text += f"{status} {product[2]} - {product[4]}₽\n"
        else:
            products_text = "📦 Нет товаров"
        
        builder.add(InlineKeyboardButton(text="➕ Добавить товар", callback_data="add_product"))
        builder.add(InlineKeyboardButton(text="🔙 К брендам", callback_data="admin_brands_list"))
        builder.adjust(1)
        return builder.as_markup()

    # Админ - управление товарами (главное меню)
    @staticmethod
    def admin_products_menu():
        builder = InlineKeyboardBuilder()
        builder.add(
            InlineKeyboardButton(text="➕ Добавить товар", callback_data="add_product"),
            InlineKeyboardButton(text="📋 Список товаров", callback_data="admin_products_list"),
            InlineKeyboardButton(text="🔙 Назад", callback_data="admin_panel")
        )
        builder.adjust(1)
        return builder.as_markup()

    # Админ - список товаров с навигацией
    @staticmethod
    def admin_products_list(products, current_index=0):
        builder = InlineKeyboardBuilder()
        
        if products:
            # Навигация
            nav_buttons = []
            if current_index > 0:
                nav_buttons.append(InlineKeyboardButton(
                    text="◀️", 
                    callback_data=f"admin_product_{current_index-1}"
                ))
            
            nav_buttons.append(InlineKeyboardButton(
                text=f"{current_index + 1}/{len(products)}", 
                callback_data="none"
            ))
            
            if current_index < len(products) - 1:
                nav_buttons.append(InlineKeyboardButton(
                    text="▶️", 
                    callback_data=f"admin_product_{current_index+1}"
                ))
            
            builder.row(*nav_buttons)
            
            # Кнопки управления
            product = products[current_index]
            status_text = "❌ Нет в наличии" if product[6] else "✅ В наличии"
            status_data = f"toggle_product_{product[0]}"
            
            builder.row(
                InlineKeyboardButton(text=status_text, callback_data=status_data),
                InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"edit_product_{product[0]}")
            )
            builder.row(
                InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"delete_product_{product[0]}"),
                InlineKeyboardButton(text="🖼️ Фото", callback_data=f"view_photo_{product[0]}")
            )
        
        builder.row(InlineKeyboardButton(text="➕ Добавить товар", callback_data="add_product"))
        builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="admin_products"))
        return builder.as_markup()

    # Админ - управление пользователями
    @staticmethod
    def admin_users_menu():
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(text="📋 Список пользователей", callback_data="admin_users_list"))
        builder.add(InlineKeyboardButton(text="🔙 Назад", callback_data="admin_panel"))
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def admin_users_list(users, current_index=0):
        builder = InlineKeyboardBuilder()
        
        if users:
            # Навигация
            nav_buttons = []
            if current_index > 0:
                nav_buttons.append(InlineKeyboardButton(
                    text="◀️", 
                    callback_data=f"admin_user_{current_index-1}"
                ))
            
            nav_buttons.append(InlineKeyboardButton(
                text=f"{current_index + 1}/{len(users)}", 
                callback_data="none"
            ))
            
            if current_index < len(users) - 1:
                nav_buttons.append(InlineKeyboardButton(
                    text="▶️", 
                    callback_data=f"admin_user_{current_index+1}"
                ))
            
            builder.row(*nav_buttons)
            
            # Кнопки управления
            user = users[current_index]
            builder.row(
                InlineKeyboardButton(text="📧 Написать", callback_data=f"message_user_{user[0]}"),
                InlineKeyboardButton(text="📊 Статистика", callback_data=f"user_stats_{user[0]}")
            )
        
        builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="admin_users"))
        return builder.as_markup()

    # Админ - управление категориями
    @staticmethod
    def admin_categories_menu(categories):
        builder = InlineKeyboardBuilder()
        for category in categories:
            status = "✅" if category[2] else "❌"
            builder.add(InlineKeyboardButton(
                text=f"{status} {category[1]}", 
                callback_data=f"toggle_category_{category[0]}"
            ))
        builder.add(InlineKeyboardButton(text="➕ Добавить категорию", callback_data="add_category"))
        builder.add(InlineKeyboardButton(text="🔙 Назад", callback_data="admin_panel"))
        builder.adjust(1)
        return builder.as_markup()

    # Панель курьера
    @staticmethod
    def courier_panel():
        builder = InlineKeyboardBuilder()
        builder.add(
            InlineKeyboardButton(text="📦 Активные доставки", callback_data="courier_active"),
            InlineKeyboardButton(text="✅ Завершенные", callback_data="courier_completed"),
            InlineKeyboardButton(text="📊 Статистика", callback_data="courier_stats"),
            InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
        )
        builder.adjust(2)
        return builder.as_markup()

    # Доставки курьера
    @staticmethod
    def courier_deliveries(orders, current_index=0):
        builder = InlineKeyboardBuilder()
        
        if orders:
            # Навигация
            nav_buttons = []
            if current_index > 0:
                nav_buttons.append(InlineKeyboardButton(
                    text="◀️", 
                    callback_data=f"courier_order_{current_index-1}"
                ))
            
            nav_buttons.append(InlineKeyboardButton(
                text=f"{current_index + 1}/{len(orders)}", 
                callback_data="none"
            ))
            
            if current_index < len(orders) - 1:
                nav_buttons.append(InlineKeyboardButton(
                    text="▶️", 
                    callback_data=f"courier_order_{current_index+1}"
                ))
            
            builder.row(*nav_buttons)
            
            # Кнопки управления доставкой
            order = orders[current_index]
            builder.row(
                InlineKeyboardButton(text="✅ Доставлено", callback_data=f"complete_delivery_{order[0]}"),
                InlineKeyboardButton(text="📋 Детали", callback_data=f"delivery_details_{order[0]}")
            )
            builder.row(
                InlineKeyboardButton(text="⚠️ Проблема", callback_data=f"delivery_issue_{order[0]}")
            )
        
        builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="courier_panel"))
        return builder.as_markup()

    # Подтверждение действий
    @staticmethod
    def confirm_keyboard(action, item_id):
        builder = InlineKeyboardBuilder()
        builder.add(
            InlineKeyboardButton(text="✅ Да", callback_data=f"confirm_{action}_{item_id}"),
            InlineKeyboardButton(text="❌ Нет", callback_data=f"cancel_{action}_{item_id}")
        )
        return builder.as_markup()

    # Отмена действия
    @staticmethod
    def cancel_keyboard(back_to):
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(text="❌ Отмена", callback_data=back_to))
        return builder.as_markup()

    # Выбор бренда для товара
    @staticmethod
    def brand_selection_keyboard(brands):
        builder = InlineKeyboardBuilder()
        for brand in brands:
            builder.add(InlineKeyboardButton(
                text=brand[2],
                callback_data=f"select_brand_{brand[0]}"
            ))
        builder.add(InlineKeyboardButton(text="❌ Отмена", callback_data="admin_products"))
        builder.adjust(1)
        return builder.as_markup()