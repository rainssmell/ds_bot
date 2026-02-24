from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram import Bot

from config import ADMIN_ID, NOTIFY_BOT_TOKEN

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
async def contact_handler(message: Message, state: FSMContext):
    contact = message.contact

    # создаём экземпляр notify-бота
    notify_bot = Bot(token=NOTIFY_BOT_TOKEN)

    text = (
        f"🔥 Новый лид\n\n"
        f"Имя: {contact.first_name}\n"
        f"Телефон: {contact.phone_number}\n"
        f"Username: @{message.from_user.username}\n"
        f"User ID: {message.from_user.id}"
    )

    # отправляем уведомление тебе
    await notify_bot.send_message(ADMIN_ID, text)

    await message.answer("Спасибо! Заявка получена ✅")
