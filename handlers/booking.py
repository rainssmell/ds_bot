from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from keyboards.addons import addons_kb
from keyboards.confirm import confirm_kb
from services.calculator import calculate_price
from config import ADMIN_ID

router = Router()

class Booking(StatesGroup):
    waiting_for_addons = State()
    waiting_for_date = State()
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_address = State()
    waiting_for_tz = State()
    waiting_for_confirm = State()


# -----------------------------
# ПАКЕТ
# -----------------------------
@router.callback_query(F.data.startswith("pkg_"))
async def choose_package(callback: types.CallbackQuery, state: FSMContext):
    package = callback.data.replace("pkg_", "")

    await state.update_data(package=package, addons=[])

    await callback.message.edit_text(
        "Пакет выбран.\nТеперь добавьте допы или нажмите «Готово»:",
        reply_markup=addons_kb()
    )

    await state.set_state(Booking.waiting_for_addons)


# -----------------------------
# ДОПЫ
# -----------------------------
@router.callback_query(Booking.waiting_for_addons)
async def choose_addons(callback: types.CallbackQuery, state: FSMContext):

    data = await state.get_data()
    addons = data["addons"]

    if callback.data == "add_mics":
        addons.append("Петлички")
    elif callback.data == "add_light":
        addons.append("Свет")
    elif callback.data == "add_extra":
        addons.append("Доп. минута монтажа")
    elif callback.data == "addons_done":
        await callback.message.edit_text("Введите дату съёмки в формате ГГГГ-ММ-ДД:")
        await state.set_state(Booking.waiting_for_date)
        return

    await state.update_data(addons=addons)
    await callback.answer("Добавлено!")


# -----------------------------
# ДАТА
# -----------------------------
@router.message(Booking.waiting_for_date)
async def get_date(msg: types.Message, state: FSMContext):
    await state.update_data(date=msg.text.strip())
    await msg.answer("Ваше имя:")
    await state.set_state(Booking.waiting_for_name)


# -----------------------------
# ИМЯ
# -----------------------------
@router.message(Booking.waiting_for_name)
async def get_name(msg: types.Message, state: FSMContext):
    await state.update_data(name=msg.text.strip())
    await msg.answer("Номер телефона:")
    await state.set_state(Booking.waiting_for_phone)


# -----------------------------
# ТЕЛЕФОН
# -----------------------------
@router.message(Booking.waiting_for_phone)
async def get_phone(msg: types.Message, state: FSMContext):
    await state.update_data(phone=msg.text.strip())
    await msg.answer("Адрес съёмки:")
    await state.set_state(Booking.waiting_for_address)


# -----------------------------
# АДРЕС
# -----------------------------
@router.message(Booking.waiting_for_address)
async def get_address(msg: types.Message, state: FSMContext):
    await state.update_data(address=msg.text.strip())
    await msg.answer("Опишите ТЗ:")
    await state.set_state(Booking.waiting_for_tz)


# -----------------------------
# ТЗ
# -----------------------------
@router.message(Booking.waiting_for_tz)
async def get_tz(msg: types.Message, state: FSMContext):
    await state.update_data(tz=msg.text.strip())

    data = await state.get_data()

    price = calculate_price(
        data["package"],
        data["addons"]
    )

    await state.update_data(price=price)

        addons_list = ", ".join(data["addons"]) if data["addons"] else "нет"

    text = (
        f"🔥 Новая заявка!\n\n"
        f"Пакет: {data['package']}\n"
        f"Допы: {addons_list}\n"
        f"Дата: {data['date']}\n"
        f"Имя: {data['name']}\n"
        f"Телефон: {data['phone']}\n"
        f"Адрес: {data['address']}\n"
        f"ТЗ: {data['tz']}\n\n"
        f"Стоимость: {data['price']} ₽"
    )

    # Пытаемся отправить админу
    try:
        await callback.bot.send_message(ADMIN_ID, text)
    except Exception:
        pass  # если ADMIN_ID кривой — просто не падаем

    # Дублируем тому, кто оставил заявку
    await callback.bot.send_message(callback.from_user.id, text)

    # Сообщение в чате с ботом
    await callback.message.edit_text(
        "Заявка создана!\n\nЯ свяжусь с вами в ближайшее время."
    )

    await state.clear()



# -----------------------------
# ПОДТВЕРЖДЕНИЕ
# -----------------------------
@router.callback_query(Booking.waiting_for_confirm)
async def confirm(callback: types.CallbackQuery, state: FSMContext):

    if callback.data == "cancel":
        await callback.message.edit_text("Заявка отменена.")
        await state.clear()
        return

    data = await state.get_data()

    addons_list = ", ".join(data["addons"]) if data["addons"] else "нет"

    # Отправляем заявку тебе (в ADMIN_ID)
    await callback.bot.send_message(
        ADMIN_ID,
        f"🔥 Новая заявка!\n\n"
        f"Пакет: {data['package']}\n"
        f"Допы: {addons_list}\n"
        f"Дата: {data['date']}\n"
        f"Имя: {data['name']}\n"
        f"Телефон: {data['phone']}\n"
        f"Адрес: {data['address']}\n"
        f"ТЗ: {data['tz']}\n\n"
        f"Стоимость: {data['price']} ₽"
    )

    # Клиенту
    await callback.message.edit_text(
        "Заявка создана!\n\nЯ свяжусь с вами в ближайшее время."
    )

    await state.clear()
