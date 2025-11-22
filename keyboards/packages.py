from aiogram.utils.keyboard import InlineKeyboardBuilder

def packages_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="3 часа (14 900 ₽)", callback_data="pkg_3h")
    kb.button(text="5 часов (19 900 ₽)", callback_data="pkg_5h")
    kb.button(text="8 часов (24 900 ₽)", callback_data="pkg_8h")
    kb.adjust(1)  # одна кнопка в ряд
    return kb.as_markup()
