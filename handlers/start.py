from aiogram import Router, types
from aiogram.filters import Command
from keyboards.packages import packages_kb

router = Router()

@router.message(Command("start"))
async def start(msg: types.Message):
    await msg.answer(
        "Привет! Я бот продакшена «Дёшево, сердито».\n\n"
        "Выбери пакет съёмки:",
        reply_markup=packages_kb()
    )
