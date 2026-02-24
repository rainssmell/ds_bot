from aiogram import Router, types, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import FSInputFile, ReplyKeyboardRemove

from keyboards.addons import addons_kb
from keyboards.confirm import confirm_kb
from keyboards.packages import packages_kb
from services.calculator import calculate_price
from services.google_sheets import append_early_lead
from config import ADMIN_ID, NOTIFY_BOT_TOKEN

router = Router()


class Booking(StatesGroup):
    waiting_for_contact = State()
    waiting_for_addons = State()
    waiting_for_date = State()
    waiting_for_address = State()
    waiting_for_tz = State()
    waiting_for_confirm = State()


ADDON_LABELS = {
    "mics": "Петлички",
    "light": "Свет",
    "extra": "Доп. минута монтажа",
}


# =============================
# КОНТАКТ
# =============================
@router.message(Booking.waiting_for_contact)
async def get_contact(msg: types.Message, state: FSMContext):
    if not msg.contact:
        await msg.answer("Пожалуйста, используйте кнопку для отправки контакта.")
        return

    phone = msg.contact.phone_number
    name = msg.contact.first_name
    username = msg.from_user.username
    user_id = msg.from_user.id

    await state.update_data(phone=phone)

    # Google early lead
    try:
        append_early_lead(
            name=name,
            phone=phone,
            username=username,
            user_id=user_id
        )
    except Exception as e:
        print("GOOGLE ERROR:", e)

    # Второй бот
    try:
        notify_bot = Bot(token=NOTIFY_BOT_TOKEN)

        text = (
            f"🔥 Новый лид\n\n"
            f"Имя: {name}\n"
            f"Телефон: {phone}\n"
            f"Username: @{username}\n"
            f"User ID: {user_id}"
        )

        await notify_bot.send_message(ADMIN_ID, text)
        await notify_bot.session.close()

    except Exception as e:
        print("NOTIFY BOT ERROR:", e)

    await msg.answer(
        "Отлично! Теперь выберите пакет съёмки:",
        reply_markup=ReplyKeyboardRemove()
    )

    await msg.answer("Выберите пакет:", reply_markup=packages_kb())

    await state.set_state(Booking.waiting_for_addons)


# =============================
# ПАКЕТ
# =============================
@router.callback_query(F.data.startswith("pkg_"))
async def choose_package(callback: types.CallbackQuery, state: FSMContext):
    package = callback.data.replace("pkg_", "")
    await state.update_data(package=package, addons=[])

    photo = FSInputFile("media/addons.png")

    await callback.message.answer_photo(
        photo,
        caption=(
            "Допы:\n\n"
            "• Петлички — +990 ₽\n"
            "• Свет — +2900 ₽\n"
            "• Доп. минута монтажа — +3900 ₽"
        )
    )

    await callback.message.answer(
        "Добавьте допы или нажмите «Готово»:",
        reply_markup=addons_kb()
    )

    await state.set_state(Booking.waiting_for_addons)
    await callback.answer()


# =============================
# ДОПЫ
# =============================
@router.callback_query(Booking.waiting_for_addons)
async def choose_addons(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    addons = data.get("addons", [])

    if callback.data == "addons_done":
        await callback.message.edit_text("Введите дату съёмки (число и месяц):")
        await state.set_state(Booking.waiting_for_date)
        await callback.answer()
        return

    mapping = {
        "add_mics": "mics",
        "add_light": "light",
        "add_extra": "extra",
    }

    code = mapping.get(callback.data)

    if code:
        if code not in addons:
            addons.append(code)
            await state.update_data(addons=addons)
            await callback.answer("Добавлено")
        else:
            await callback.answer("Уже добавлено")


# =============================
# ДАТА
# =============================
@router.message(Booking.waiting_for_date)
async def get_date(msg: types.Message, state: FSMContext):
    await state.update_data(date=msg.text.strip())
    await msg.answer("Адрес съёмки:")
    await state.set_state(Booking.waiting_for_address)


# =============================
# АДРЕС
# =============================
@router.message(Booking.waiting_for_address)
async def get_address(msg: types.Message, state: FSMContext):
    await state.update_data(address=msg.text.strip())
    await msg.answer("Опишите ТЗ:")
    await state.set_state(Booking.waiting_for_tz)


# =============================
# ТЗ
# =============================
@router.message(Booking.waiting_for_tz)
async def get_tz(msg: types.Message, state: FSMContext):
    await state.update_data(tz=msg.text.strip())
    data = await state.get_data()

    price = calculate_price(
        data["package"],
        data.get("addons", [])
    )

    await state.update_data(price=price)

    addons_list = (
        ", ".join(ADDON_LABELS[c] for c in data.get("addons", []))
        if data.get("addons") else "нет"
    )

    await msg.answer(
        f"Проверьте заявку:\n\n"
        f"Пакет: {data['package']}\n"
        f"Допы: {addons_list}\n"
        f"Дата: {data['date']}\n"
        f"Телефон: {data['phone']}\n"
        f"Адрес: {data['address']}\n"
        f"ТЗ: {data['tz']}\n\n"
        f"Стоимость: {price} ₽",
        reply_markup=confirm_kb()
    )

    await state.set_state(Booking.waiting_for_confirm)


# =============================
# ПОДТВЕРЖДЕНИЕ
# =============================
@router.callback_query(Booking.waiting_for_confirm)
async def final_confirm(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "cancel":
        await callback.message.edit_text("Заявка отменена.")
        await state.clear()
        await callback.answer()
        return

    data = await state.get_data()

    addons_list = (
        ", ".join(ADDON_LABELS[c] for c in data.get("addons", []))
        if data.get("addons") else "нет"
    )

    text = (
        "🔥 Новая заявка!\n\n"
        f"Пакет: {data['package']}\n"
        f"Допы: {addons_list}\n"
        f"Дата: {data['date']}\n"
        f"Телефон: {data['phone']}\n"
        f"Адрес: {data['address']}\n"
        f"ТЗ: {data['tz']}\n\n"
        f"Стоимость: {data['price']} ₽"
    )

    await callback.bot.send_message(ADMIN_ID, text)

    await callback.message.edit_text(
        "Заявка создана! Я свяжусь с вами."
    )

    await state.clear()
    await callback.answer()
