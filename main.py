import os
import asyncio
import sys
from aiohttp import web
from aiogram import Bot, Dispatcher
from core.config import settings
from core.logger import logger
from core.database import db_manager
from data.collector import data_collector

# Import routers
from telegram.handlers import start, market, ai, paper, health

async def handle_ping(request):
    return web.json_response({
        "status": "ok",
        "service": "XAUUSD Trading Bot",
        "message": "Bot is running and healthy!"
    })

async def start_health_server():
    port = int(os.getenv("PORT", "8080"))
    app = web.Application()
    app.router.add_get("/", handle_ping)
    app.router.add_get("/health", handle_ping)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"Health check HTTP web server listening on 0.0.0.0:{port}")
    return runner

async def main():
    logger.info("XAUUSD Real-Time Market Intelligence & AI Platform ishga tushmoqda...")
    settings.validate()

    # 1. Initialize DB
    await db_manager.init_db()

    # 2. Start Background Data Collector Service
    collector_task = asyncio.create_task(data_collector.start())

    # 3. Start Health Check HTTP Server (for Render / UptimeRobot)
    web_runner = await start_health_server()

    # 4. Setup Telegram Bot & Dispatcher
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
        await web_runner.cleanup()
        data_collector.stop()
        collector_task.cancel()
        await bot.session.close()
        logger.info("Tizim to'xtatildi.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
