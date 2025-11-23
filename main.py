import os
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from handlers.start import router as start_router
from handlers.booking import router as booking_router


async def healthcheck(request):
    return web.Response(text="ok")


async def run_bot():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(start_router)
    dp.include_router(booking_router)
    print("Бот запущен!")
    await dp.start_polling(bot)


async def main():
    # HTTP-сервер для Render (чтобы был открытый порт)
    app = web.Application()
    app.router.add_get("/", healthcheck)

    runner = web.AppRunner(app)
    await runner.setup()

    port = int(os.getenv("PORT", "10000"))
    site = web.TCPSite(runner, host="0.0.0.0", port=port)
    await site.start()
    print(f"HTTP healthcheck запущен на порту {port}")

    # параллельно запускаем бота
    asyncio.create_task(run_bot())

    # держим процесс живым
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())