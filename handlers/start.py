from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from handlers.booking import Booking

router = Router()

contact_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Отправить контакт", request_contact=True)]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    await state.set_state(Booking.waiting_for_contact)

    await message.answer(
        "Чтобы продолжить, пожалуйста, отправьте ваш контакт 👇",
        reply_markup=contact_keyboard
    )
