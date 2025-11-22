import asyncio
from aiogram import Bot, Dispatcher

from config import BOT_TOKEN

# роутеры
from handlers.start import router as start_router
from handlers.booking import router as booking_router


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # подключаем роутеры
    dp.include_router(start_router)
    dp.include_router(booking_router)

    print("Бот запущен!")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
