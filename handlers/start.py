from aiogram import Router, F, Bot
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from config import ADMIN_ID

router = Router()

contact_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Отправить контакт", request_contact=True)]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)


@router.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        "Чтобы продолжить, пожалуйста, отправьте ваш контакт 👇",
        reply_markup=contact_keyboard
    )


@router.message(F.contact)
async def contact_handler(
    message: Message,
    state: FSMContext,
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

    # 👉 уведомление через ВТОРОЙ бот
    await notify_bot.send_message(ADMIN_ID, text)

    # убираем клавиатуру
    await message.answer("Контакт получен ✅")

    # 👉 запускаем дальнейший сценарий
    from handlers.booking import start_booking_flow
    await start_booking_flow(message, state)
