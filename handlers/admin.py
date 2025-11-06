from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
import json

from config import ADMIN_IDS
from database.database import db
from keyboards.keyboards import Keyboards
from states.states import AdminStates

router = Router()

# Проверка админских прав
async def check_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

# Админ команда
@router.message(Command("admin"))
async def admin_command(message: Message):
    if not await check_admin(message.from_user.id):
        await message.answer("❌ Доступ запрещен!")
        return
    
    admin_text = """
👑 <b>ПАНЕЛЬ АДМИНИСТРАТОРА</b>

Управление магазином:
"""
    await message.answer(admin_text, reply_markup=Keyboards.admin_panel())

# Админ панель
@router.callback_query(F.data == "admin_panel")
async def admin_panel(callback: CallbackQuery):
    if not await check_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещен!")
        return
    
    admin_text = """
👑 <b>ПАНЕЛЬ АДМИНИСТРАТОРА</b>

Управление магазином:
"""
    await callback.message.edit_text(admin_text, reply_markup=Keyboards.admin_panel())

# Статистика админа
@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    if not await check_admin(callback.from_user.id):
        return
    
    stats = await db.get_admin_stats()
    
    stats_text = f"""
📊 <b>СТАТИСТИКА МАГАЗИНА</b>

👥 <b>Пользователи:</b> {stats['total_users']}
📦 <b>Всего заказов:</b> {stats['total_orders']}
💰 <b>Общая выручка:</b> {stats['total_revenue']:.2f}₽
⏳ <b>Ожидают обработки:</b> {stats['pending_orders']}
📈 <b>Заказов сегодня:</b> {stats['today_orders']}

<b>Статистика обновляется в реальном времени</b>
    """
    
    await callback.message.edit_text(stats_text, reply_markup=Keyboards.admin_stats())
    await callback.answer()

# Управление заказами - главное меню
@router.callback_query(F.data == "admin_orders")
async def admin_orders(callback: CallbackQuery):
    if not await check_admin(callback.from_user.id):
        return
    
    orders = await db.get_pending_orders()
    
    orders_text = f"""
📦 <b>УПРАВЛЕНИЕ ЗАКАЗАМИ</b>

⏳ <b>Заказов ожидает:</b> {len(orders)}

Выберите действие:
"""
    await callback.message.edit_text(orders_text, reply_markup=Keyboards.admin_orders_menu())
    await callback.answer()

# Список заказов с навигацией
@router.callback_query(F.data == "admin_orders_list")
async def admin_orders_list(callback: CallbackQuery):
    if not await check_admin(callback.from_user.id):
        return
    
    orders = await db.get_pending_orders()
    
    if orders:
        # Показываем первый заказ
        await show_single_order(callback, orders, 0)
    else:
        await callback.message.edit_text(
            "📦 <b>Нет заказов, ожидающих обработки</b>",
            reply_markup=Keyboards.admin_orders_menu()
        )
    await callback.answer()

# Функция для показа одного заказа
async def show_single_order(callback: CallbackQuery, orders: list, current_index: int):
    if not orders or current_index >= len(orders):
        return
    
    order = orders[current_index]
    
    # Безопасно получаем данные заказа
    order_id = order[0]
    user_id = order[1]
    products_data = order[2]  # JSON строка с товарами
    total_amount = order[4]
    status = order[3]
    order_date = order[5]
    
    # Получаем информацию о пользователе из базы
    user = await db.get_user(user_id)
    user_name = user[2] if user else "Неизвестно"
    user_phone = user[4] if user else "Неизвестно"
    user_city = user[3] if user else "Неизвестно"
    username = user[1] if user and user[1] else "Не указан"
    
    # Парсим товары
    try:
        product_ids = json.loads(products_data)
        products_info = []
        for product_id in product_ids:
            product = await db.get_product(product_id)
            if product:
                products_info.append(f"• {product[2]} - {product[4]}₽")
        products_text = "\n".join(products_info) if products_info else "Товары не найдены"
    except:
        products_text = "Ошибка загрузки товаров"
    
    order_text = f"""
📦 <b>ЗАКАЗ #{order_id}</b>

👤 <b>Клиент:</b> {user_name}
🔗 <b>Username:</b> @{username if username != 'Не указан' else 'отсутствует'}
📱 <b>Телефон:</b> {user_phone}
📍 <b>Город:</b> {user_city}
💵 <b>Сумма:</b> {total_amount}₽
📅 <b>Дата:</b> {order_date}
📊 <b>Статус:</b> {status}

<b>Товары:</b>
{products_text}
    """
    
    await callback.message.edit_text(
        order_text, 
        reply_markup=Keyboards.admin_orders_list(orders, current_index, user_id, username)
    )

# Функция для показа одного заказа
async def show_single_order(callback: CallbackQuery, orders: list, current_index: int):
    if not orders or current_index >= len(orders):
        return
    
    order = orders[current_index]
    
    # Безопасно получаем данные заказа
    order_id = order[0]
    user_id = order[1]
    products_data = order[2]  # JSON строка с товарами
    total_amount = order[4]
    status = order[3]
    order_date = order[5]
    
    # Получаем информацию о пользователе
    user = await db.get_user(user_id)
    user_name = user[2] if user else "Неизвестно"
    user_phone = user[4] if user else "Неизвестно"
    user_city = user[3] if user else "Неизвестно"
    
    # Парсим товары
    try:
        product_ids = json.loads(products_data)
        products_info = []
        for product_id in product_ids:
            product = await db.get_product(product_id)
            if product:
                products_info.append(f"• {product[2]} - {product[4]}₽")
        products_text = "\n".join(products_info) if products_info else "Товары не найдены"
    except:
        products_text = "Ошибка загрузки товаров"
    
    order_text = f"""
📦 <b>ЗАКАЗ #{order_id}</b>

👤 <b>Клиент:</b> {user_name}
📱 <b>Телефон:</b> {user_phone}
📍 <b>Город:</b> {user_city}
💵 <b>Сумма:</b> {total_amount}₽
📅 <b>Дата:</b> {order_date}
📊 <b>Статус:</b> {status}

<b>Товары:</b>
{products_text}
    """
    
    await callback.message.edit_text(
        order_text, 
        reply_markup=Keyboards.admin_orders_list(orders, current_index)
    )

# Навигация по заказам
@router.callback_query(F.data.startswith("admin_order_"))
async def process_admin_order_navigation(callback: CallbackQuery):
    if not await check_admin(callback.from_user.id):
        return
    
    current_index = int(callback.data.split("_")[2])
    orders = await db.get_pending_orders()
    await show_single_order(callback, orders, current_index)
    await callback.answer()


# Управление брендами - главное меню
@router.callback_query(F.data == "admin_brands")
async def admin_brands(callback: CallbackQuery):
    if not await check_admin(callback.from_user.id):
        return
    
    brands = await db.get_all_brands()
    
    brands_text = f"""
🏷️ <b>УПРАВЛЕНИЕ БРЕНДАМИ</b>

📊 <b>Всего брендов:</b> {len(brands)}

Выберите действие:
"""
    await callback.message.edit_text(brands_text, reply_markup=Keyboards.admin_brands_menu())
    await callback.answer()

# Список брендов с навигацией
@router.callback_query(F.data == "admin_brands_list")
async def admin_brands_list(callback: CallbackQuery):
    if not await check_admin(callback.from_user.id):
        return
    
    brands = await db.get_all_brands()
    
    if brands:
        await show_admin_brand(callback, 0)
    else:
        await callback.message.edit_text(
            "🏷️ <b>Бренды не найдены</b>\n\nДобавьте первый бренд!",
            reply_markup=Keyboards.admin_brands_menu()
        )
    await callback.answer()

# Функция для показа бренда
async def show_admin_brand(callback: CallbackQuery, current_index: int):
    brands = await db.get_all_brands()
    
    if brands and 0 <= current_index < len(brands):
        brand = brands[current_index]
        
        brand_text = f"""
🏷️ <b>БРЕНД: {brand[2]}</b>

📁 <b>Категория:</b> {brand[5]}
📝 <b>Описание:</b> {brand[3] or 'Нет описания'}
📊 <b>Статус:</b> {'✅ Активен' if brand[4] else '❌ Скрыт'}

🆔 <b>ID:</b> {brand[0]}
        """
        
        await callback.message.edit_text(
            brand_text,
            reply_markup=Keyboards.admin_brands_list_navigation(brands, current_index)
        )

@router.callback_query(F.data.startswith("admin_brand_"))
async def process_admin_brand_navigation(callback: CallbackQuery):
    if not await check_admin(callback.from_user.id):
        return
    
    current_index = int(callback.data.split("_")[2])
    await show_admin_brand(callback, current_index)
    await callback.answer()

# Добавление бренда - Шаг 1: Название
@router.callback_query(F.data == "add_brand")
async def add_brand_start(callback: CallbackQuery, state: FSMContext):
    if not await check_admin(callback.from_user.id):
        return
    
    await callback.message.edit_text(
        "🏷️ <b>ДОБАВЛЕНИЕ БРЕНДА</b>\n\n"
        "Введите название нового бренда:",
        reply_markup=Keyboards.cancel_keyboard("admin_brands")
    )
    await state.set_state(AdminStates.waiting_for_brand_name)
    await callback.answer()

@router.message(AdminStates.waiting_for_brand_name)
async def process_brand_name(message: Message, state: FSMContext):
    brand_name = message.text
    await state.update_data(brand_name=brand_name)
    
    await message.answer(
        "📝 <b>Введите описание бренда:</b>\n\n"
        "Можно добавить краткое описание или нажать /skip чтобы пропустить:",
        reply_markup=Keyboards.cancel_keyboard("admin_brands")
    )
    await state.set_state(AdminStates.waiting_for_brand_description)

@router.message(AdminStates.waiting_for_brand_description)
async def process_brand_description(message: Message, state: FSMContext):
    brand_description = message.text
    
    # Если пропустили описание
    if brand_description == "/skip":
        brand_description = ""
    
    await state.update_data(brand_description=brand_description)
    
    await message.answer(
        "📁 <b>Выберите категорию для бренда:</b>",
        reply_markup=Keyboards.admin_category_selection()
    )
    await state.set_state(AdminStates.waiting_for_brand_category)

# Используем уникальный префикс для категорий в админке
@router.callback_query(AdminStates.waiting_for_brand_category, F.data.startswith("admin_category_"))
async def process_brand_category(callback: CallbackQuery, state: FSMContext):
    category_id = callback.data.split("_")[2]  # admin_category_{id}
    user_data = await state.get_data()
    brand_name = user_data['brand_name']
    brand_description = user_data.get('brand_description', '')
    
    brand_id = await db.add_brand(category_id, brand_name, brand_description)
    
    await callback.message.edit_text(
        f"✅ <b>Бренд '{brand_name}' успешно добавлен! (ID: {brand_id})</b>",
        reply_markup=Keyboards.admin_brands_menu()
    )
    await state.clear()
    await callback.answer()

# Управление пользователями - главное меню
@router.callback_query(F.data == "admin_users")
async def admin_users(callback: CallbackQuery):
    if not await check_admin(callback.from_user.id):
        return
    
    users = await db.get_all_users()
    
    users_text = f"""
👤 <b>УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ</b>

📊 <b>Всего пользователей:</b> {len(users)}

Выберите действие:
"""
    await callback.message.edit_text(users_text, reply_markup=Keyboards.admin_users_menu())
    await callback.answer()

# Список пользователей
@router.callback_query(F.data == "admin_users_list")
async def admin_users_list(callback: CallbackQuery):
    if not await check_admin(callback.from_user.id):
        return
    
    users = await db.get_all_users()
    
    if users:
        await show_admin_user(callback, 0)
    else:
        await callback.message.edit_text(
            "👤 <b>Пользователи не найдены</b>",
            reply_markup=Keyboards.admin_users_menu()
        )
    await callback.answer()

# Функция для показа пользователя
async def show_admin_user(callback: CallbackQuery, current_index: int):
    users = await db.get_all_users()
    
    if users and 0 <= current_index < len(users):
        user = users[current_index]
        
        user_text = f"""
👤 <b>ПОЛЬЗОВАТЕЛЬ</b>

🆔 <b>ID:</b> {user[0]}
👤 <b>Имя:</b> {user[2]}
🔗 <b>Username:</b> @{user[1] or 'отсутствует'}
📱 <b>Телефон:</b> {user[4]}
📍 <b>Город:</b> {user[3]}
💎 <b>Реф. код:</b> {user[5]}

📊 <b>Статистика:</b>
💼 Заказов: {user[10] or 0}
💰 Потрачено: {user[8] or 0}₽
🎁 Бонус: {'✅ Доступен' if user[9] else '❌ Не доступен'}

📅 <b>Регистрация:</b> {user[7]}
        """
        
        await callback.message.edit_text(
            user_text,
            reply_markup=Keyboards.admin_users_list_navigation(users, current_index)
        )

@router.callback_query(F.data.startswith("admin_user_"))
async def process_admin_user_navigation(callback: CallbackQuery):
    if not await check_admin(callback.from_user.id):
        return
    
    current_index = int(callback.data.split("_")[2])
    await show_admin_user(callback, current_index)
    await callback.answer()

# Обработчик для статистики пользователя
@router.callback_query(F.data.startswith("user_stats_"))
async def user_stats_handler(callback: CallbackQuery):
    if not await check_admin(callback.from_user.id):
        return
    
    user_id = int(callback.data.split("_")[2])
    user = await db.get_user(user_id)
    
    if user:
        user_orders = await db.get_user_orders(user_id)
        total_orders = len(user_orders)
        total_spent = user[8] or 0
        
        stats_text = f"""
📊 <b>СТАТИСТИКА ПОЛЬЗОВАТЕЛЯ</b>

👤 <b>Пользователь:</b> {user[2]}
💼 <b>Всего заказов:</b> {total_orders}
💰 <b>Потрачено:</b> {total_spent}₽
📅 <b>Регистрация:</b> {user[7]}

<b>Последние заказы:</b>
"""
        # Показываем последние 5 заказов
        for i, order in enumerate(user_orders[:5]):
            status_icon = "✅" if order[3] == "confirmed" else "⏳" if order[3] == "pending" else "❌"
            stats_text += f"\n{status_icon} Заказ #{order[0]} - {order[4]}₽ - {order[3]}"
        
        await callback.message.edit_text(stats_text, reply_markup=Keyboards.admin_users_menu())
    
    await callback.answer()

# Обработчик для случая когда нет username у пользователя
@router.callback_query(F.data == "no_user_username")
async def no_user_username_handler(callback: CallbackQuery):
    await callback.answer("❌ У пользователя нет username")

# Переключение статуса бренда
@router.callback_query(F.data.startswith("toggle_brand_"))
async def toggle_brand(callback: CallbackQuery):
    if not await check_admin(callback.from_user.id):
        return
    
    brand_id = int(callback.data.split("_")[2])
    brand = await db.get_brand(brand_id)
    
    if brand:
        new_status = not brand[4]
        await db.toggle_brand(brand_id, new_status)
        status_text = "активирован" if new_status else "скрыт"
        await callback.answer(f"✅ Бренд {status_text}!")
        
        # Обновляем текущий вид
        brands = await db.get_all_brands()
        current_index = next((i for i, b in enumerate(brands) if b[0] == brand_id), 0)
        await show_admin_brand(callback, current_index)

# Удаление бренда
@router.callback_query(F.data.startswith("delete_brand_"))
async def delete_brand(callback: CallbackQuery):
    if not await check_admin(callback.from_user.id):
        return
    
    brand_id = int(callback.data.split("_")[2])
    brand = await db.get_brand(brand_id)
    
    if brand:
        # Проверяем есть ли товары у этого бренда
        products = await db.get_products_by_brand(brand_id)
        if products:
            await callback.answer("❌ Нельзя удалить бренд с товарами!")
            return
        
        await db.delete_brand(brand_id)
        await callback.answer("🗑️ Бренд удален!")
        await admin_brands_list(callback)

# Просмотр товаров бренда
@router.callback_query(F.data.startswith("brand_products_"))
async def show_brand_products(callback: CallbackQuery):
    if not await check_admin(callback.from_user.id):
        return
    
    brand_id = int(callback.data.split("_")[2])
    products = await db.get_products_by_brand(brand_id)
    brand = await db.get_brand(brand_id)
    
    if products:
        products_text = f"📦 <b>ТОВАРЫ БРЕНДА: {brand[2]}</b>\n\n"
        for product in products:
            status = "✅" if product[6] else "❌"
            products_text += f"{status} {product[2]} - {product[4]}₽ (ID: {product[0]})\n"
    else:
        products_text = f"📦 <b>В бренде '{brand[2]}' нет товаров</b>"
    
    await callback.message.edit_text(
        products_text,
        reply_markup=Keyboards.admin_brand_products(brand_id, products)
    )
    await callback.answer()
    

# Управление товарами - главное меню
@router.callback_query(F.data == "admin_products")
async def admin_products(callback: CallbackQuery):
    if not await check_admin(callback.from_user.id):
        return
    
    products = await db.get_all_products()
    
    products_text = f"""
📦 <b>УПРАВЛЕНИЕ ТОВАРАМИ</b>

📊 <b>Всего товаров:</b> {len(products)}

Выберите действие:
"""
    await callback.message.edit_text(products_text, reply_markup=Keyboards.admin_products_menu())

# Список товаров с навигацией
@router.callback_query(F.data == "admin_products_list")
async def admin_products_list(callback: CallbackQuery):
    if not await check_admin(callback.from_user.id):
        return
    
    products = await db.get_all_products()
    
    if products:
        await show_admin_product(callback, products, 0)
    else:
        await callback.message.edit_text(
            "📦 <b>Товары не найдены</b>\n\nДобавьте первый товар!",
            reply_markup=Keyboards.admin_products_menu()
        )

@router.callback_query(F.data.startswith("admin_product_"))
async def show_admin_product(callback: CallbackQuery, products=None, current_index=None):
    if not await check_admin(callback.from_user.id):
        return
    
    if products is None:
        products = await db.get_all_products()
        current_index = int(callback.data.split("_")[2])
    
    if products and 0 <= current_index < len(products):
        product = products[current_index]
        
        product_text = f"""
📦 <b>ТОВАР: {product[2]}</b>

🏷️ <b>Бренд:</b> {product[8]}
📁 <b>Категория:</b> {product[9]}
💵 <b>Цена:</b> {product[4]}₽
📝 <b>Описание:</b> {product[3]}
📊 <b>Статус:</b> {'✅ В наличии' if product[6] else '❌ Нет в наличии'}

🆔 <b>ID:</b> {product[0]}
        """
        
        # Если есть фото, отправляем фото с описанием
        if product[5]:
            await callback.message.delete()
            await callback.message.answer_photo(
                photo=product[5],
                caption=product_text,
                reply_markup=Keyboards.admin_products_list(products, current_index)
            )
        else:
            await callback.message.edit_text(
                product_text,
                reply_markup=Keyboards.admin_products_list(products, current_index)
            )

# Обновляем переключение статуса товара
@router.callback_query(F.data.startswith("toggle_product_"))
async def toggle_product(callback: CallbackQuery):
    if not await check_admin(callback.from_user.id):
        return
    
    product_id = int(callback.data.split("_")[2])
    product = await db.get_product(product_id)
    
    if product:
        new_status = not product[6]
        await db.toggle_product_availability(product_id, new_status)
        status_text = "в наличии" if new_status else "нет в наличии"
        await callback.answer(f"✅ Товар теперь {status_text}!")
        await admin_products_list(callback)

# Добавление товара - Шаг 1: Выбор бренда
@router.callback_query(F.data == "add_product")
async def add_product_start(callback: CallbackQuery, state: FSMContext):
    if not await check_admin(callback.from_user.id):
        return
    
    brands = await db.get_all_brands()
    
    if not brands:
        await callback.answer("❌ Сначала добавьте бренды!")
        return
    
    await callback.message.edit_text(
        "🏷️ <b>ВЫБЕРИТЕ БРЕНД ДЛЯ ТОВАРА</b>",
        reply_markup=Keyboards.brand_selection_keyboard(brands)
    )
    await state.set_state(AdminStates.waiting_for_product_brand)

@router.callback_query(AdminStates.waiting_for_product_brand, F.data.startswith("select_brand_"))
async def process_product_brand(callback: CallbackQuery, state: FSMContext):
    brand_id = int(callback.data.split("_")[2])
    await state.update_data(brand_id=brand_id)
    
    await callback.message.edit_text(
        "📦 <b>ДОБАВЛЕНИЕ ТОВАРА</b>\n\n"
        "Введите название товара:",
        reply_markup=Keyboards.cancel_keyboard("admin_products")
    )
    await state.set_state(AdminStates.waiting_for_product_name)

@router.message(AdminStates.waiting_for_product_name)
async def process_product_name(message: Message, state: FSMContext):
    product_name = message.text
    await state.update_data(product_name=product_name)
    
    await message.answer(
        "📝 <b>Введите описание товара:</b>",
        reply_markup=Keyboards.cancel_keyboard("admin_products")
    )
    await state.set_state(AdminStates.waiting_for_product_description)

@router.message(AdminStates.waiting_for_product_description)
async def process_product_description(message: Message, state: FSMContext):
    product_description = message.text
    await state.update_data(product_description=product_description)
    
    await message.answer(
        "💵 <b>Введите цену товара (в рублях):</b>\n\n"
        "Пример: 1500 или 1999.99",
        reply_markup=Keyboards.cancel_keyboard("admin_products")
    )
    await state.set_state(AdminStates.waiting_for_product_price)

@router.message(AdminStates.waiting_for_product_price)
async def process_product_price(message: Message, state: FSMContext):
    try:
        price = float(message.text)
        await state.update_data(price=price)
        
        await message.answer(
            "🖼️ <b>Отправьте фото товара:</b>\n\n"
            "Пришлите изображение товара как фото (не как файл)",
            reply_markup=Keyboards.cancel_keyboard("admin_products")
        )
        await state.set_state(AdminStates.waiting_for_product_photo)
    except ValueError:
        await message.answer("❌ Неверный формат цены! Введите число:")

@router.message(AdminStates.waiting_for_product_photo, F.photo)
async def process_product_photo(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    user_data = await state.get_data()
    
    brand_id = user_data['brand_id']
    product_name = user_data['product_name']
    product_description = user_data['product_description']
    price = user_data['price']
    
    # Добавляем товар в базу
    product_id = await db.add_product(brand_id, product_name, product_description, price, photo_id)
    
    await message.answer(
        f"✅ <b>Товар '{product_name}' успешно добавлен! (ID: {product_id})</b>",
        reply_markup=Keyboards.admin_products_menu()
    )
    await state.clear()

# Редактирование товара
@router.callback_query(F.data.startswith("edit_product_"))
async def edit_product_start(callback: CallbackQuery, state: FSMContext):
    if not await check_admin(callback.from_user.id):
        return
    
    product_id = int(callback.data.split("_")[2])
    product = await db.get_product(product_id)
    
    if product:
        await state.update_data(
            product_id=product_id,
            current_name=product[2],
            current_description=product[3],
            current_price=product[4]
        )
        
        await callback.message.edit_text(
            f"✏️ <b>РЕДАКТИРОВАНИЕ ТОВАРА</b>\n\n"
            f"Текущее название: <b>{product[2]}</b>\n"
            f"Текущее описание: <b>{product[3]}</b>\n"
            f"Текущая цена: <b>{product[4]}₽</b>\n\n"
            "Введите новое название товара:",
            reply_markup=Keyboards.cancel_keyboard("admin_products_list")
        )
        await state.set_state(AdminStates.waiting_for_product_name)


# Удаление товара
@router.callback_query(F.data.startswith("delete_product_"))
async def delete_product(callback: CallbackQuery):
    if not await check_admin(callback.from_user.id):
        return
    
    product_id = int(callback.data.split("_")[2])
    product = await db.get_product(product_id)
    
    if product:
        await db.delete_product(product_id)
        await callback.answer("🗑️ Товар удален!")
        await admin_products_list(callback)

# Управление пользователями - главное меню
@router.callback_query(F.data == "admin_users")
async def admin_users(callback: CallbackQuery):
    if not await check_admin(callback.from_user.id):
        return
    
    users = await db.get_all_users()
    
    users_text = f"""
👤 <b>УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ</b>

📊 <b>Всего пользователей:</b> {len(users)}

Выберите действие:
"""
    await callback.message.edit_text(users_text, reply_markup=Keyboards.admin_users_menu())

# Список пользователей
@router.callback_query(F.data == "admin_users_list")
async def admin_users_list(callback: CallbackQuery):
    if not await check_admin(callback.from_user.id):
        return
    
    users = await db.get_all_users()
    
    if users:
        await show_admin_user(callback, users, 0)
    else:
        await callback.message.edit_text(
            "👤 <b>Пользователи не найдены</b>",
            reply_markup=Keyboards.admin_users_menu()
        )

@router.callback_query(F.data.startswith("admin_user_"))
async def show_admin_user(callback: CallbackQuery, users=None, current_index=None):
    if not await check_admin(callback.from_user.id):
        return
    
    if users is None:
        users = await db.get_all_users()
        current_index = int(callback.data.split("_")[2])
    
    if users and 0 <= current_index < len(users):
        user = users[current_index]
        
        user_text = f"""
👤 <b>ПОЛЬЗОВАТЕЛЬ</b>

🆔 <b>ID:</b> {user[0]}
👤 <b>Имя:</b> {user[2]}
📱 <b>Телефон:</b> {user[4]}
📍 <b>Город:</b> {user[3]}
💎 <b>Реф. код:</b> {user[5]}

📊 <b>Статистика:</b>
💼 Заказов: {user[10] or 0}
💰 Потрачено: {user[8] or 0}₽
🎁 Бонус: {'✅ Доступен' if user[9] else '❌ Не доступен'}

📅 <b>Регистрация:</b> {user[7]}
        """
        
        await callback.message.edit_text(
            user_text,
            reply_markup=Keyboards.admin_users_list(users, current_index)
        )

# Управление категориями
@router.callback_query(F.data == "admin_categories")
async def admin_categories(callback: CallbackQuery):
    if not await check_admin(callback.from_user.id):
        return
    
    categories = await db.get_all_categories()
    
    categories_text = "📁 <b>УПРАВЛЕНИЕ КАТЕГОРИЯМИ</b>\n\n"
    for category in categories:
        status = "✅" if category[2] else "❌"
        categories_text += f"{status} <b>{category[1]}</b> (ID: {category[0]})\n"
    
    await callback.message.edit_text(
        categories_text,
        reply_markup=Keyboards.admin_categories_menu(categories)
    )

# Переключение категории
@router.callback_query(F.data.startswith("toggle_category_"))
async def toggle_category(callback: CallbackQuery):
    if not await check_admin(callback.from_user.id):
        return
    
    category_id = callback.data.split("_")[2]
    categories = await db.get_all_categories()
    current_category = next((c for c in categories if c[0] == category_id), None)
    
    if current_category:
        new_status = not current_category[2]
        await db.toggle_category(category_id, new_status)
        status_text = "активирована" if new_status else "скрыта"
        await callback.answer(f"✅ Категория {status_text}!")
        await admin_categories(callback)