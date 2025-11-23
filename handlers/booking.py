from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from aiogram.types import FSInputFile, InputMediaPhoto

from keyboards.addons import addons_kb
from keyboards.confirm import confirm_kb
from services.calculator import calculate_price
from config import ADMIN_ID

ADDON_LABELS = {
    "mics": "Петлички",
    "light": "Свет",
    "extra": "Доп. минута монтажа",
}

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

    # отправляем альбом с тремя допами
    media = [
        InputMediaPhoto(
            media=FSInputFile("media/petli.png"),
            caption="Петлички — +990 ₽"
        ),
        InputMediaPhoto(
            media=FSInputFile("media/svet.png"),
            caption="Свет (3 источника) — +2900 ₽"
        ),
        InputMediaPhoto(
            media=FSInputFile("media/montazh.png"),
            caption="Доп. минута монтажа — +3900 ₽"
        ),
    ]

    await callback.message.answer_media_group(media)

    # сообщение с кнопками выбора допов
    await callback.message.answer(
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
    addons = data.get("addons", [])

    code = None
    if callback.data == "add_mics":
        code = "mics"
    elif callback.data == "add_light":
        code = "light"
    elif callback.data == "add_extra":
        code = "extra"
    elif callback.data == "addons_done":
        await callback.message.edit_text("Введите дату съёмки — число и месяц:")
        await state.set_state(Booking.waiting_for_date)
        return

    if code:
        if code not in addons:
            addons.append(code)
            await state.update_data(addons=addons)
            await callback.answer("Добавлено!")
        else:
            await callback.answer("Уже добавлено", show_alert=False)


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
    # сохраняем ТЗ
    await state.update_data(tz=msg.text.strip())
    data = await state.get_data()

    # считаем цену
    price = calculate_price(
        data["package"],
        data.get("addons", [])
    )
    # кладём цену в стейт, чтобы потом забрать в final_confirm
    await state.update_data(price=price)

  addon_codes = data.get("addons", [])
addons_list = (
    ", ".join(ADDON_LABELS[c] for c in addon_codes)
    if addon_codes else "нет"
)

    # показываем пользователю итог
    await msg.answer(
        f"Проверьте заявку:\n\n"
        f"Пакет: {data['package']}\n"
        f"Допы: {addons_list}\n"
        f"Дата: {data['date']}\n"
        f"Имя: {data['name']}\n"
        f"Телефон: {data['phone']}\n"
        f"Адрес: {data['address']}\n"
        f"ТЗ: {data['tz']}\n\n"
        f"Стоимость: {price} ₽",
        reply_markup=confirm_kb()
    )

    await state.set_state(Booking.waiting_for_confirm)


# -----------------------------
# ПОДТВЕРЖДЕНИЕ
# -----------------------------
@router.callback_query(Booking.waiting_for_confirm)
async def final_confirm(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "cancel":
        await callback.message.edit_text("Заявка отменена.")
        await state.clear()
        return

    data = await state.get_data()

    addons_list = ", ".join(data.get("addons", [])) if data.get("addons") else "нет"

    text = (
        "🔥 Новая заявка!\n\n"
        f"Пакет: {data['package']}\n"
        f"Допы: {addons_list}\n"
        f"Дата: {data['date']}\n"
        f"Имя: {data['name']}\n"
        f"Телефон: {data['phone']}\n"
        f"Адрес: {data['address']}\n"
        f"ТЗ: {data['tz']}\n\n"
        f"Стоимость: {data['price']} ₽"
    )

    # отправляем тебе в личку
    await callback.bot.send_message(ADMIN_ID, text)

    # отвечаем клиенту
    await callback.message.edit_text(
        "Заявка создана! Я свяжусь с вами в ближайшее время."
    )

    await state.clear()
    await callback.answer()