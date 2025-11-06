from aiogram import Router, F
from aiogram.types import CallbackQuery

from config import COURIER_IDS
from database.database import db
from keyboards.keyboards import Keyboards

router = Router()

# Проверка прав курьера
async def check_courier(user_id: int) -> bool:
    return user_id in COURIER_IDS

# Панель курьера
@router.callback_query(F.data == "courier_panel")
async def courier_panel(callback: CallbackQuery):
    if not await check_courier(callback.from_user.id):
        await callback.answer("❌ Доступ запрещен!")
        return
    
    courier_text = f"""
🚗 <b>ПАНЕЛЬ КУРЬЕРА</b>

👋 Добро пожаловать, {callback.from_user.full_name}!

Управление доставками:
"""
    await callback.message.edit_text(courier_text, reply_markup=Keyboards.courier_panel())

# Активные доставки
@router.callback_query(F.data == "courier_active")
async def courier_active(callback: CallbackQuery):
    if not await check_courier(callback.from_user.id):
        return
    
    courier_id = callback.from_user.id
    orders = await db.get_orders_by_courier(courier_id)
    
    if orders:
        await show_courier_order(callback, orders, 0)
    else:
        await callback.message.edit_text(
            "📦 <b>Нет активных доставок</b>\n\nОжидайте назначения заказов.",
            reply_markup=Keyboards.courier_panel()
        )

@router.callback_query(F.data.startswith("courier_order_"))
async def show_courier_order(callback: CallbackQuery, orders=None, current_index=None):
    if not await check_courier(callback.from_user.id):
        return
    
    if orders is None:
        courier_id = callback.from_user.id
        orders = await db.get_orders_by_courier(courier_id)
        current_index = int(callback.data.split("_")[2])
    
    if orders and 0 <= current_index < len(orders):
        order = orders[current_index]
        user = await db.get_user(order[1])
        
        order_text = f"""
🚗 <b>ДОСТАВКА #{order[0]}</b>

👤 <b>Клиент:</b> {user[2]}
📱 <b>Телефон:</b> {user[4]}
📍 <b>Адрес:</b> {order[8]}
⏰ <b>Время:</b> {order[7]}
👨‍💼 <b>Описание курьера:</b> {order[9]}

💵 <b>Сумма заказа:</b> {order[4]}₽
📅 <b>Дата заказа:</b> {order[5]}
        """
        
        await callback.message.edit_text(
            order_text,
            reply_markup=Keyboards.courier_deliveries(orders, current_index)
        )

# Завершение доставки
@router.callback_query(F.data.startswith("complete_delivery_"))
async def complete_delivery(callback: CallbackQuery):
    if not await check_courier(callback.from_user.id):
        return
    
    order_id = int(callback.data.split("_")[2])
    await db.complete_order(order_id)
    
    await callback.answer("✅ Доставка завершена!")
    await courier_active(callback)

# Завершенные доставки
@router.callback_query(F.data == "courier_completed")
async def courier_completed(callback: CallbackQuery):
    if not await check_courier(callback.from_user.id):
        return
    
    # Здесь можно добавить логику для показа завершенных доставок
    await callback.message.edit_text(
        "✅ <b>ЗАВЕРШЕННЫЕ ДОСТАВКИ</b>\n\n"
        "Функция в разработке...",
        reply_markup=Keyboards.courier_panel()
    )

# Статистика курьера
@router.callback_query(F.data == "courier_stats")
async def courier_stats(callback: CallbackQuery):
    if not await check_courier(callback.from_user.id):
        return
    
    courier_id = callback.from_user.id
    orders = await db.get_orders_by_courier(courier_id)
    completed_orders = [o for o in orders if o[10]]  # is_completed
    
    stats_text = f"""
📊 <b>СТАТИСТИКА КУРЬЕРА</b>

👤 <b>Курьер:</b> {callback.from_user.full_name}

📦 <b>Активные доставки:</b> {len(orders) - len(completed_orders)}
✅ <b>Завершенные доставки:</b> {len(completed_orders)}
💰 <b>Общая сумма доставок:</b> {sum(o[4] for o in completed_orders)}₽

🌟 <b>Отличная работа! Продолжайте в том же духе!</b>
    """
    
    await callback.message.edit_text(stats_text, reply_markup=Keyboards.courier_panel())