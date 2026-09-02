import asyncio
import sys
from aiogram import Bot, Dispatcher
from core.config import settings
from core.logger import logger
from core.database import db_manager
from data.collector import data_collector

# Import routers
from telegram.handlers import start, market, ai, paper, health

async def main():
    logger.info("XAUUSD Real-Time Market Intelligence & AI Platform ishga tushmoqda...")
    settings.validate()

    # 1. Initialize DB
    await db_manager.init_db()

    # 2. Start Background Data Collector Service
    collector_task = asyncio.create_task(data_collector.start())

    # 3. Setup Telegram Bot & Dispatcher
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN topilmadi! Bot ishga tusha olmaydi. .env faylini to'ldiring.")
        return

    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    dp = Dispatcher()

    # Register Routers
    dp.include_router(start.router)
    dp.include_router(market.router)
    dp.include_router(ai.router)
    dp.include_router(paper.router)
    dp.include_router(health.router)

    try:
        logger.info("Telegram Bot Polling boshlanmoqda...")
        await dp.start_polling(bot)
    finally:
        data_collector.stop()
        collector_task.cancel()
        await bot.session.close()
        logger.info("Tizim to'xtatildi.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
