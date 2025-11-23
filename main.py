import os
import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from handlers.start import router as start_router
from handlers.booking import router as booking_router

logging.basicConfig(level=logging.INFO)


async def healthcheck(request):
    return web.Response(text="ok")


async def start_bot():
    logging.info("=== ИНИЦИАЛИЗАЦИЯ БОТА ===")

    try:
        bot = Bot(token=BOT_TOKEN)
        dp = Dispatcher(storage=MemoryStorage())

        dp.include_router(start_router)
        dp.include_router(booking_router)

        logging.info("=== POLLING START ===")
        await dp.start_polling(bot)
    except Exception as e:
        logging.exception(f"ОШИБКА В РАБОТЕ ПОЛЛИНГА: {e}")
        await asyncio.sleep(5)
        logging.info("=== ПОВТОРНЫЙ ЗАПУСК ПОЛЛИНГА ===")
        asyncio.create_task(start_bot())


async def main():
    logging.info("=== main() loading ===")

    # HTTP healthcheck для Render
    app = web.Application()
    app.router.add_get("/", healthcheck)

    runner = web.AppRunner(app)
    await runner.setup()

    port = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)

    await site.start()
    logging.info(f"=== HTTP healthcheck порт {port} ===")

    # параллельно запускаем бота
    asyncio.create_task(start_bot())

    # держим процесс живым
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    logging.info("=== entry ===")
    asyncio.run(main())
