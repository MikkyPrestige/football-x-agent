"""Inline keyboards for Telegram bot."""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def copy_buttons(draft_id: int, variants: list[str]) -> InlineKeyboardMarkup:
    """Create a row of Copy buttons, one per variant."""
    buttons = [
        InlineKeyboardButton(f"Copy V{i+1}", callback_data=f"copy_{draft_id}_{i}")
        for i in range(len(variants))
    ]
    return InlineKeyboardMarkup([buttons])
