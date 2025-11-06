from aiogram.fsm.state import State, StatesGroup

class Registration(StatesGroup):
    waiting_for_city = State()
    waiting_for_phone = State()

class AdminStates(StatesGroup):
    waiting_for_brand_name = State()
    waiting_for_brand_category = State()
    waiting_for_brand_description = State()
    waiting_for_product_name = State()
    waiting_for_product_brand = State()
    waiting_for_product_price = State()
    waiting_for_product_description = State()
    waiting_for_product_photo = State()
    waiting_for_category_name = State()

class OrderStates(StatesGroup):
    waiting_for_delivery_info = State()
    waiting_for_courier_assignment = State()

class UserStates(StatesGroup):
    waiting_for_complaint = State()