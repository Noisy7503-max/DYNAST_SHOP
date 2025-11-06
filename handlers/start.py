from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InputMediaPhoto

from config import ADMIN_IDS, COURIER_IDS
from database.database import db
from keyboards.keyboards import Keyboards
from states.states import Registration

router = Router()

# User cart storage
user_carts = {}

async def show_main_menu(message: types.Message, user_id: int):
    user = await db.get_user(user_id)
    
    # Проверяем, что user не None и имеет достаточно полей
    if not user:
        # Если пользователь не найден, просим зарегистрироваться
        await message.answer("❌ Пользователь не найден. Пожалуйста, пройдите регистрацию через /start")
        return
    
    is_admin = user_id in ADMIN_IDS
    is_courier = user_id in COURIER_IDS
    
    # Безопасное получение данных пользователя
    username = user[1] or "Не указан"
    full_name = user[2] or "Не указано"
    city = user[3] or "Не указан"
    phone = user[4] or "Не указан"
    referral_code = user[5] or "Не указан"
    total_spent = user[8] or 0
    has_bonus = user[9] if len(user) > 9 else False
    orders_count = user[10] if len(user) > 10 else 0
    
    # Получаем количество товаров в корзине
    cart_count = len(user_carts.get(user_id, []))
    
    menu_text = f"""
🏠 <b>Главное меню | DYNAST SHOP</b>

👋 Приветствуем, {full_name}!

📍 <b>Город:</b> {city}
📱 <b>Телефон:</b> {phone}
💎 <b>Реф. код:</b> <code>{referral_code}</code>

💼 <b>Заказов:</b> {orders_count}
💰 <b>Потрачено:</b> {total_spent}₽
🛒 <b>Товаров в корзине:</b> {cart_count}
🎁 <b>Бонус:</b> {'✅ Доступен' if has_bonus else '❌ Не доступен'}
    """
    
    keyboard = Keyboards.main_menu(user_id, is_admin, is_courier, cart_count > 0)
    
    if isinstance(message, CallbackQuery):
        # Для callback всегда отправляем новое сообщение
        await message.message.answer(menu_text, reply_markup=keyboard)
    else:
        await message.answer(menu_text, reply_markup=keyboard)

# Start command with beautiful design
@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    args = message.text.split()
    referral_code = args[1] if len(args) > 1 else None
    
    user = await db.get_user(user_id)
    
    welcome_text = """
🎉 <b>Добро пожаловать в DYNAST SHOP!</b> 🎉

🌟 <i>Премиальные вейп-устройства и аксессуары</i>

Мы рады приветствовать вас в нашем магазине!
Для начала работы пройдите быструю регистрацию.
    """
    
    if not user:
        await state.set_state(Registration.waiting_for_city)
        if referral_code:
            await state.update_data(referral_code=referral_code)
        
        await message.answer(welcome_text)
        await message.answer(
            "📍 <b>Выберите ваш город:</b>",
            reply_markup=Keyboards.cities_keyboard()
        )
    else:
        await show_main_menu(message, user_id)

# City selection
@router.callback_query(F.data.startswith("city_"))
async def process_city(callback: CallbackQuery, state: FSMContext):
    city = callback.data.split("_", 1)[1]
    await state.update_data(city=city)
    await state.set_state(Registration.waiting_for_phone)
    
    await callback.message.edit_text(
        f"📍 <b>Выбран город:</b> {city}\n\n"
        "📱 <b>Теперь поделитесь вашим номером телефона:</b>\n\n"
        "<i>Нажмите кнопку ниже или напишите номер вручную в формате +7XXXXXXXXXX</i>",
        reply_markup=Keyboards.request_phone()
    )

# Phone sharing
@router.callback_query(F.data == "send_phone")
async def request_phone(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📱 <b>Отправьте ваш номер телефона</b>\n\n"
        "Используйте кнопку \"📱 Отправить телефон\" или напишите номер вручную в формате:\n"
        "<code>+79991234567</code>"
    )

@router.message(Registration.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    phone = message.text
    user_data = await state.get_data()
    
    # Generate referral code
    referral_code = f"ref{message.from_user.id}"
    
    await db.add_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name,
        city=user_data['city'],
        phone=phone,
        referral_code=referral_code
    )
    
    await state.clear()
    
    # Welcome message after registration
    welcome_registered = f"""
✅ <b>Регистрация завершена!</b>

👋 <b>Добро пожаловать в DYNAST SHOP, {message.from_user.full_name}!</b>

📍 <b>Ваш город:</b> {user_data['city']}
📱 <b>Телефон:</b> {phone}
💎 <b>Реферальный код:</b> <code>{referral_code}</code>

🎁 <i>Приглашайте друзей и получайте бонусы!</i>
    """
    
    await message.answer(welcome_registered)
    await show_main_menu(message, message.from_user.id)

@router.callback_query(F.data == "main_menu")
async def back_to_main(callback: CallbackQuery):
    await show_main_menu(callback, callback.from_user.id)