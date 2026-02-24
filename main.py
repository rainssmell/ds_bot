import asyncio
import logging

from aiogram import Bot, Dispatcher
from config import BOT_TOKEN, NOTIFY_BOT_TOKEN
from handlers.start import router as start_router
from handlers.booking import router as booking_router


async def main():
    logging.basicConfig(level=logging.INFO)

    # основной бот
    bot = Bot(token=BOT_TOKEN)

    # второй бот для уведомлений
    notify_bot = Bot(token=NOTIFY_BOT_TOKEN)

    dp = Dispatcher()

    # передаём notify_bot в хендлеры
    dp["notify_bot"] = notify_bot

    # регистрируем роутеры
    dp.include_router(start_router)
    dp.include_router(booking_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
