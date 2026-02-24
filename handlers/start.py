from aiogram import Router, F, Bot
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from config import ADMIN_ID
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


@router.message(F.contact)
async def contact_handler(
    message: Message,
    notify_bot: Bot
):
    contact = message.contact

    text = (
        f"🔥 Новый лид\n\n"
        f"Имя: {contact.first_name}\n"
        f"Телефон: {contact.phone_number}\n"
        f"Username: @{message.from_user.username}\n"
        f"User ID: {message.from_user.id}"
    )

    # ранний лид через второй бот
    await notify_bot.send_message(ADMIN_ID, text)

    # ничего больше НЕ делаем
    # FSM в booking.py сам обработает контакт дальше
