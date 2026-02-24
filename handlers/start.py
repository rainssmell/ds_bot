from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext

from handlers.booking import Booking

router = Router()


def contact_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Отправить контакт", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )


@router.message(Command("start"))
async def start(msg: types.Message, state: FSMContext):
    await state.clear()

    await msg.answer(
        "Привет! Перед началом работы отправьте, пожалуйста, ваш контакт.",
        reply_markup=contact_kb()
    )

    await state.set_state(Booking.waiting_for_contact)
