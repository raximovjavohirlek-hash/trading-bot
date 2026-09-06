import os
import asyncio
import sys
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramUnauthorizedError
from core.config import settings
from core.logger import logger
from core.database import db_manager
from data.collector import data_collector
from analytics.signal_monitor import signal_monitor

# Import routers and middlewares
from telegram.handlers import start, market, ai, paper, health, admin
from telegram.middlewares.auth import AuthMiddleware

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
    token = settings.TELEGRAM_BOT_TOKEN.strip()
    if not token or token == "your_token_here":
        logger.error("❌ TELEGRAM_BOT_TOKEN topilmadi yoki defolt qiymatda ('your_token_here')!")
        logger.error("👉 Render Dashboard -> Environment tabida TELEGRAM_BOT_TOKEN ga bot tokeningizni kiriting.")
        logger.info("HTTP Web server faol turibdi...")
        await asyncio.Event().wait()
        return

    bot = Bot(token=token)
    dp = Dispatcher()

    # 5. Attach Access Control & Authorization Middleware
    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())

    # 6. Start Signal Monitor Background Service (Scans 24/7 for 90-100% setups)
    signal_monitor.set_bot(bot)
    signal_monitor_task = asyncio.create_task(signal_monitor.start())

    # Register Routers (admin & start first, then features)
    dp.include_router(admin.router)
    dp.include_router(start.router)
    dp.include_router(market.router)
    dp.include_router(ai.router)
    dp.include_router(paper.router)
    dp.include_router(health.router)

    try:
        logger.info("Telegram Bot Polling va 90-100% Avtomatik Signal Monitoring boshlanmoqda...")
        await dp.start_polling(bot)
    except TelegramUnauthorizedError:
        logger.error("❌ XATO: TELEGRAM_BOT_TOKEN noto'g'ri! Telegram 'Unauthorized' (401) qaytardi.")
        logger.error("👉 Render Dashboard -> Environment -> TELEGRAM_BOT_TOKEN qiymatini @BotFather bergan token bilan almashtiring.")
        logger.info("HTTP Web Server faol turibdi (Health check uchun)...")
        await asyncio.Event().wait()
    finally:
        signal_monitor.stop()
        signal_monitor_task.cancel()
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
