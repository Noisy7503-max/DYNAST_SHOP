from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from config import MANAGER_USERNAME
from database.database import db
from keyboards.keyboards import Keyboards

router = Router()

@router.callback_query(F.data == "personal_cabinet")
async def personal_cabinet(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    
    cabinet_text = f"""
👤 <b>ЛИЧНЫЙ КАБИНЕТ</b>

👋 <b>{user[2]}</b>
📍 <b>Город:</b> {user[3]}
📱 <b>Телефон:</b> {user[4]}

📊 <b>Статистика:</b>
💼 Заказов: {user[10] or 0}
💰 Потрачено: {user[8] or 0}₽
🎁 Бонус: {'✅ Доступен' if user[9] else '❌ Не доступен'}

💎 <b>Реферальный код:</b>
<code>{user[5]}</code>

<i>Дарите друзьям скидку 20% на первый заказ!</i>
    """
    
    await callback.message.edit_text(cabinet_text, reply_markup=Keyboards.personal_cabinet())

@router.callback_query(F.data == "order_history")
async def order_history(callback: CallbackQuery):
    user_id = callback.from_user.id
    orders = await db.get_user_orders(user_id)
    
    if orders:
        text = "📦 <b>ИСТОРИЯ ЗАКАЗОВ</b>\n\n"
        for order in orders:
            status_icons = {
                'pending': '⏳',
                'confirmed': '✅', 
                'rejected': '❌',
                'completed': '🚗'
            }
            status_emoji = status_icons.get(order[3], '📦')
            text += f"{status_emoji} <b>Заказ #{order[0]}</b>\n"
            text += f"💵 Сумма: {order[4]} руб.\n"
            text += f"📅 Дата: {order[5]}\n"
            text += f"📊 Статус: {order[3]}\n\n"
    else:
        text = "📦 <b>У вас пока нет заказов</b>\n\nСделайте первый заказ в нашем магазине! 🛍️"
    
    await callback.message.edit_text(text, reply_markup=Keyboards.personal_cabinet())

@router.callback_query(F.data == "referral")
async def referral_system(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    
    referral_text = f"""
🎁 <b>РЕФЕРАЛЬНАЯ СИСТЕМА</b>

💎 <b>Ваш реферальный код:</b>
<code>{user[5]}</code>

🤝 <b>Как это работает:</b>
1. Делитесь вашим реферальным кодом с друзьями
2. Друг делает заказ на сумму от 500₽
3. Вы получаете скидку 20% на следующий заказ!

💰 <b>Ваша статистика:</b>
• Приглашено друзей: 0
• Доступных бонусов: {1 if user[9] else 0}

📢 <b>Пригласительная ссылка:</b>
<code>https://t.me/your_bot?start={user[5]}</code>

<i>Бонус активируется после первого заказа приглашенного друга!</i>
    """
    
    await callback.message.edit_text(referral_text, reply_markup=Keyboards.personal_cabinet())

@router.callback_query(F.data == "about")
async def about_us(callback: CallbackQuery):
    about_text = """
🏢 <b>О МАГАЗИНЕ DYNAST SHOP</b>

Мы - DYNAST SHOP, поставщик премиальных вейп-устройств и аксессуаров. 
Наша миссия - предоставлять клиентам только качественную продукцию от проверенных брендов.

<b>Наши преимущества:</b>
✅ Только оригинальная продукция
🚚 Быстрая доставка по всей России  
💎 Эксклюзивные бренды
🎁 Бонусная программа
📞 Круглосуточная поддержка

<b>Мы работаем с 2024 года и доверены сотням клиентов!</b>
    """
    await callback.message.edit_text(about_text, reply_markup=Keyboards.about_and_contacts())

@router.callback_query(F.data == "support")
async def support(callback: CallbackQuery):
    support_text = f"""
💬 <b>ТЕХНИЧЕСКАЯ ПОДДЕРЖКА</b>

По всем вопросам обращайтесь к нашему менеджеру:

👤 <b>Менеджер:</b> {MANAGER_USERNAME}
⏰ <b>Время работы:</b> 24/7

Мы всегда рады помочь вам с выбором товара, оформлением заказа или решением любых вопросов!

📞 <b>Не стесняйтесь писать!</b>
    """
    await callback.message.edit_text(support_text, reply_markup=Keyboards.about_and_contacts())

@router.callback_query(F.data == "contacts")
async def contacts(callback: CallbackQuery):
    contacts_text = f"""
📞 <b>КОНТАКТЫ DYNAST SHOP</b>

<b>Свяжитесь с нами:</b>

👤 <b>Менеджер:</b> {MANAGER_USERNAME}
📧 <b>Email:</b> dynastshop@gmail.ru
📱 <b>Телефон:</b> +7XXXXXXXXXX

<b>Время работы поддержки:</b>
🕒 Круглосуточно

<b>Мы всегда на связи!</b> 😊
    """
    await callback.message.edit_text(contacts_text, reply_markup=Keyboards.about_and_contacts())