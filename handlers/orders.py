from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database.database import db
from keyboards.keyboards import Keyboards
from states.states import UserStates

router = Router()

# Детали заказа
@router.callback_query(F.data.startswith("order_details_"))
async def order_details(callback: CallbackQuery):
    order_id = int(callback.data.split("_")[2])
    order = await db.get_order(order_id)
    
    if order:
        user = await db.get_user(order[1])
        
        order_text = f"""
📋 <b>ДЕТАЛИ ЗАКАЗА #{order[0]}</b>

👤 <b>Клиент:</b> {user[2]}
📱 <b>Телефон:</b> {user[4]}
📍 <b>Город:</b> {user[3]}

💵 <b>Сумма:</b> {order[4]}₽
📅 <b>Дата:</b> {order[5]}
📊 <b>Статус:</b> {order[3]}

"""
        
        if order[6]:  # courier_id
            courier = await db.get_user(order[6])
            order_text += f"🚗 <b>Курьер:</b> {courier[2] if courier else 'Не назначен'}\n"
        
        if order[7]:  # delivery_time
            order_text += f"⏰ <b>Время доставки:</b> {order[7]}\n"
        
        if order[8]:  # delivery_location
            order_text += f"📍 <b>Место доставки:</b> {order[8]}\n"
        
        if order[9]:  # courier_description
            order_text += f"👨‍💼 <b>Описание курьера:</b> {order[9]}\n"
        
        await callback.message.edit_text(order_text, reply_markup=Keyboards.admin_panel())

# Назначение курьера
@router.callback_query(F.data.startswith("assign_courier_"))
async def assign_courier(callback: CallbackQuery):
    order_id = int(callback.data.split("_")[2])
    
    # Здесь можно добавить логику для выбора курьера из списка
    # Пока просто назначаем текущего пользователя как курьера
    await db.assign_courier(order_id, callback.from_user.id)
    
    await callback.answer("🚗 Курьер назначен!")
    
    # Обновляем список заказов
    from handlers.admin import admin_orders
    await admin_orders(callback)

# Жалоба на курьера
@router.callback_query(F.data.startswith("complain_"))
async def start_complaint(callback: CallbackQuery, state: FSMContext):
    order_id = int(callback.data.split("_")[1])
    
    await state.update_data(order_id=order_id)
    await state.set_state(UserStates.waiting_for_complaint)
    
    await callback.message.edit_text(
        "⚠️ <b>ОПИШИТЕ ПРОБЛЕМУ</b>\n\n"
        "Пожалуйста, подробно опишите проблему, которая возникла с доставкой:",
        reply_markup=Keyboards.cancel_keyboard("courier_panel")
    )

@router.message(UserStates.waiting_for_complaint)
async def process_complaint(message: Message, state: FSMContext):
    user_data = await state.get_data()
    order_id = user_data['order_id']
    
    await db.add_complaint(order_id, message.from_user.id, message.text)
    
    await message.answer(
        "✅ <b>ЖАЛОБА ОТПРАВЛЕНА</b>\n\n"
        "Спасибо за обратную связь! Мы рассмотрим вашу жалобу в ближайшее время.",
        reply_markup=Keyboards.main_menu(message.from_user.id)
    )
    
    await state.clear()