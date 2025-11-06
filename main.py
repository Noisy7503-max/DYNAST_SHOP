import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN
from database.database import db
from handlers import start, user, catalog, admin, courier, orders


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    # Initialize bot and dispatcher
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
    dp = Dispatcher()

    # Register all routers
    dp.include_router(start.router)
    dp.include_router(user.router)
    dp.include_router(catalog.router)
    dp.include_router(admin.router)
    dp.include_router(courier.router)
    dp.include_router(orders.router)


    # Create database tables
    await db.create_tables()
    
    logger.info("Bot started successfully!")
    
    # Start polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())