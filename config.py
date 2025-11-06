import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_IDS = [int(x) for x in os.getenv('ADMIN_IDS', '').split(',') if x]
COURIER_IDS = [int(x) for x in os.getenv('COURIER_IDS', '').split(',') if x]
MANAGER_USERNAME = os.getenv('MANAGER_USERNAME', '@dynastsh0p')

# Database configuration
DB_NAME = os.getenv('DB_PATH')

# Cities available for registration
CITIES = ['Харцызск', 'Донецк', 'Макеевка', 'Иловайск', 'Торез']

# Referral system
REFERRAL_BONUS_THRESHOLD = 500  # Минимальная сумма для получения бонуса
REFERRAL_DISCOUNT = 20  # Скидка 20%

# Категории товаров
CATEGORIES = {
    'disposable': '🔥 Одноразки',
    'devices': '⚡ Устройства',
    'liquids': '💧 Жидкости',
    'accessories': '🔧 Аксессуары'
}