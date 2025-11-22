from aiogram import Router, types
from keyboards.packages import packages_kb

router = Router()

@router.message(commands=["start"])
async def start(msg: types.Message):
    await msg.answer(
        "Привет! Я бот продакшена «Дёшево, сердито».\n\n"
        "Выбери пакет съёмки:",
        reply_markup=packages_kb()
    )
