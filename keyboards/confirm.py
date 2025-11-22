from aiogram.utils.keyboard import InlineKeyboardBuilder

def confirm_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="Подтвердить запись", callback_data="confirm")
    kb.button(text="Отменить", callback_data="cancel")
    kb.adjust(1)
    return kb.as_markup()
