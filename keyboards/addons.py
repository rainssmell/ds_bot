from aiogram.utils.keyboard import InlineKeyboardBuilder

def addons_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="Петлички +990 ₽", callback_data="add_mics")
    kb.button(text="Свет (3 источника) +2900 ₽", callback_data="add_light")
    kb.button(text="Доп. минута монтажа +3900 ₽", callback_data="add_extra")
    kb.button(text="Готово", callback_data="addons_done")
    kb.adjust(1)
    return kb.as_markup()
