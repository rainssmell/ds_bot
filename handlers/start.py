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
async def start_handler(message: Message, state: FSMContext):
    await message.answer(
        "Чтобы продолжить, пожалуйста, отправьте ваш контакт 👇",
        reply_markup=contact_keyboard
    )


@router.message(F.contact)
async def contact_handler(message: Message, bot: Bot, state: FSMContext):
    contact = message.contact

    text = (
        f"🔥 Новый лид\n\n"
        f"Имя: {contact.first_name}\n"
        f"Телефон: {contact.phone_number}\n"
        f"Username: @{message.from_user.username}\n"
        f"User ID: {message.from_user.id}"
    )

    # уведомление тебе
    await bot.send_message(ADMIN_ID, text)

    await message.answer("Спасибо! Заявка получена ✅")
