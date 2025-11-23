import os
import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from handlers.start import router as start_router
from handlers.booking import router as booking_router

logging.basicConfig(level=logging.DEBUG)


async def healthcheck(request):
    return web.Response(text="ok")


async def run_bot():
    logging.info("=== run_bot() START ===")
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start_router)
    dp.include_router(booking_router)

    logging.info("=== Starting polling ===")
    await dp.start_polling(bot)


async def main():
    logging.info("=== main() START ===")

    app = web.Application()
    app.router.add_get("/", healthcheck)

    runner = web.AppRunner(app)
    await runner.setup()

    port = int(os.getenv("PORT", "10000"))
    site = web.TCPSite(runner, host="0.0.0.0", port=port)

    await site.start()
    logging.info(f"=== HTTP healthcheck запущен на порту {port} ===")

    asyncio.create_task(run_bot())

    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    logging.info("=== entrypoint ===")
    asyncio.run(main())
