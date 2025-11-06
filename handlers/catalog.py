from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InputMediaPhoto
from aiogram.exceptions import TelegramBadRequest

from database.database import db
from keyboards.keyboards import Keyboards
from handlers.start import user_carts, show_main_menu

router = Router()

@router.callback_query(F.data == "catalog")
async def show_catalog(callback: CallbackQuery):
    catalog_text = """
🛍️ <b>КАТАЛОГ ТОВАРОВ</b>

Выберите категорию:
"""
    # Всегда отправляем новое сообщение для навигации
    await callback.message.answer(catalog_text, reply_markup=Keyboards.catalog_categories())
    await callback.answer()

@router.callback_query(F.data.startswith("category_"))
async def show_brands(callback: CallbackQuery):
    category_id = callback.data.split("_")[1]
    from config import CATEGORIES
    category_name = CATEGORIES.get(category_id, "Категория")
    brands = await db.get_brands_by_category(category_id)
    
    if brands:
        brands_text = f"🏷️ <b>БРЕНДЫ | {category_name}</b>\n\nВыберите бренд:"
        # Всегда отправляем новое сообщение для навигации
        await callback.message.answer(brands_text, reply_markup=Keyboards.brands_menu(brands, category_id))
    else:
        await callback.message.answer(
            f"😔 <b>В категории '{category_name}' пока нет брендов</b>",
            reply_markup=Keyboards.catalog_categories()
        )
    await callback.answer()

@router.callback_query(F.data.startswith("brand_"))
async def show_products(callback: CallbackQuery):
    brand_id = int(callback.data.split("_")[1])
    products = await db.get_products_by_brand(brand_id)
    
    if products:
        await show_product_detail(callback, brand_id, 0)
    else:
        await callback.message.answer(
            "😔 <b>В этом бренде пока нет товаров</b>",
            reply_markup=Keyboards.catalog_categories()
        )
    await callback.answer()

@router.callback_query(F.data.startswith("product_"))
async def show_product_detail(callback: CallbackQuery, brand_id: int = None, product_index: int = None):
    if brand_id is None:
        parts = callback.data.split("_")
        brand_id = int(parts[1])
        product_index = int(parts[2])
    
    products = await db.get_products_by_brand(brand_id)
    
    if products and 0 <= product_index < len(products):
        product = products[product_index]
        user_id = callback.from_user.id
        
        # Check if product is in cart
        in_cart = False
        if user_id in user_carts:
            in_cart = any(p[0] == product[0] for p in user_carts[user_id])
        
        # Определяем статус наличия
        is_available = product[6]  # is_available поле
        status_text = "✅ В наличии" if is_available else "❌ Нет в наличии"
        status_emoji = "✅" if is_available else "❌"
        
        caption = f"""
📦 <b>{product[2]}</b>

📝 <b>Описание:</b>
{product[3]}

💵 <b>Цена:</b> {product[4]} руб.
{status_emoji} <b>Статус:</b> {status_text}
🆔 <b>Артикул:</b> {product[0]}

{'🛒 <i>Товар уже в корзине</i>' if in_cart else ''}
        """
        
        try:
            # Если сообщение уже содержит фото, редактируем его
            if callback.message.photo:
                await callback.message.edit_media(
                    media=InputMediaPhoto(media=product[5], caption=caption),
                    reply_markup=Keyboards.products_menu(products, brand_id, product_index, in_cart, is_available)
                )
            else:
                # Иначе отправляем новое сообщение с фото
                await callback.message.answer_photo(
                    photo=product[5],
                    caption=caption,
                    reply_markup=Keyboards.products_menu(products, brand_id, product_index, in_cart, is_available)
                )
        except TelegramBadRequest:
            # Если не удалось редактировать, отправляем новое сообщение
            await callback.message.answer_photo(
                photo=product[5],
                caption=caption,
                reply_markup=Keyboards.products_menu(products, brand_id, product_index, in_cart, is_available)
            )
    await callback.answer()

@router.callback_query(F.data.startswith("add_to_cart_"))
async def add_to_cart(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[3])
    user_id = callback.from_user.id
    
    if user_id not in user_carts:
        user_carts[user_id] = []
    
    product = await db.get_product(product_id)
    if product and not any(p[0] == product_id for p in user_carts[user_id]):
        user_carts[user_id].append(product)
        await callback.answer("✅ Товар добавлен в корзину!")
        
        # Обновляем сообщение с товаром
        products = await db.get_products_by_brand(product[1])
        current_index = next((i for i, p in enumerate(products) if p[0] == product_id), 0)
        await show_product_detail(callback, product[1], current_index)
    else:
        await callback.answer("⚠️ Товар уже в корзине!")

@router.callback_query(F.data.startswith("quick_order_"))
async def quick_order(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id
    
    product = await db.get_product(product_id)
    if product:
        if user_id not in user_carts:
            user_carts[user_id] = []
        user_carts[user_id] = [product]  # Replace cart with this product
        
        cart_text = "📦 <b>БЫСТРЫЙ ЗАКАЗ</b>\n\n"
        total = 0
        for item in user_carts[user_id]:
            cart_text += f"• {item[2]} - {item[4]}₽\n"
            total += item[4]
        
        cart_text += f"\n💵 <b>Итого:</b> {total}₽"
        cart_text += f"\n\n📍 <b>Город:</b> {(await db.get_user(user_id))[3]}"
        cart_text += f"\n📱 <b>Телефон:</b> {(await db.get_user(user_id))[4]}"
        cart_text += "\n\n✅ <b>Все верно?</b>"
        
        # Отправляем новое сообщение для корзины
        await callback.message.answer(cart_text, reply_markup=Keyboards.cart_keyboard(user_carts[user_id]))
    await callback.answer()

@router.callback_query(F.data == "checkout")
async def checkout(callback: CallbackQuery):
    user_id = callback.from_user.id
    
    if user_id not in user_carts or not user_carts[user_id]:
        await callback.answer("❌ Корзина пуста!")
        return
    
    cart_items = user_carts[user_id]
    total = sum(item[4] for item in cart_items)
    
    # Create order
    order_id = await db.create_order(user_id, [item[0] for item in cart_items], total)
    
    # Update user spent amount
    await db.update_user_spent(user_id, total)
    
    # Clear cart
    user_carts[user_id] = []
    
    order_text = f"""
✅ <b>ЗАКАЗ ОФОРМЛЕН!</b>

📦 <b>Заказ #{order_id}</b>
💵 <b>Сумма:</b> {total}₽
📍 <b>Город:</b> {(await db.get_user(user_id))[3]}
📱 <b>Телефон:</b> {(await db.get_user(user_id))[4]}

🕒 <b>Статус:</b> Ожидает подтверждения
👨‍💼 <b>Менеджер свяжется с вами в ближайшее время</b>

<i>Спасибо за заказ! 😊</i>
    """
    
    await callback.message.answer(order_text, reply_markup=Keyboards.main_menu(user_id))
    await callback.answer()

@router.callback_query(F.data == "clear_cart")
async def clear_cart(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id in user_carts:
        user_carts[user_id] = []
    await callback.answer("🗑️ Корзина очищена!")
    await show_main_menu(callback, user_id)

# Просмотр корзины
@router.callback_query(F.data == "view_cart")
async def view_cart(callback: CallbackQuery):
    user_id = callback.from_user.id
    
    if user_id not in user_carts or not user_carts[user_id]:
        cart_text = "🛒 <b>ВАША КОРЗИНА ПУСТА</b>\n\nДобавьте товары из каталога!"
        await callback.message.answer(cart_text, reply_markup=Keyboards.catalog_categories())
    else:
        cart_items = user_carts[user_id]
        cart_text = "🛒 <b>ВАША КОРЗИНА</b>\n\n"
        total = 0
        
        for item in cart_items:
            cart_text += f"📦 {item[2]}\n"
            cart_text += f"💵 {item[4]}₽\n"
            cart_text += f"🆔 Артикул: {item[0]}\n\n"
            total += item[4]
        
        cart_text += f"💵 <b>Итого:</b> {total}₽"
        cart_text += f"\n\n📍 <b>Город:</b> {(await db.get_user(user_id))[3]}"
        cart_text += f"\n📱 <b>Телефон:</b> {(await db.get_user(user_id))[4]}"
        
        await callback.message.answer(cart_text, reply_markup=Keyboards.cart_keyboard(cart_items))
    await callback.answer()

@router.callback_query(F.data == "not_available")
async def not_available_handler(callback: CallbackQuery):
    await callback.answer("❌ Этот товар временно отсутствует в наличии")