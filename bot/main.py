"""Telegram bot entry point. Run with: python -m bot.main"""
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from telegram import BotCommand
from config.settings import TELEGRAM_BOT_TOKEN
from bot.handlers import (
    start, queue_callback, stats, rules, addrule, source_status,
    posted, metrics, button_handler, backup_cmd, livecheck
)

async def set_commands(app: Application):
    """Register Telegram command suggestions on startup."""
    commands = [
        BotCommand("start", "Welcome message"),
        BotCommand("queue", "View pending normal drafts"),
        BotCommand("posted", "Mark a draft as posted"),
        BotCommand("metrics", "Enter engagement numbers"),
        BotCommand("stats", "Top & bottom tweets (likes default)"),
        BotCommand("rules", "View / approve style rules"),
        BotCommand("addrule", "Add a manual rule"),
        BotCommand("source_status", "Check news source health"),
        BotCommand("backup", "Backup database to Telegram"),
        BotCommand("livecheck", "Force check for live matches"),
    ]
    await app.bot.set_my_commands(commands)

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("queue", queue_callback))
    app.add_handler(CommandHandler("posted", posted))
    app.add_handler(CommandHandler("metrics", metrics))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("rules", rules))
    app.add_handler(CommandHandler("addrule", addrule))
    app.add_handler(CommandHandler("source_status", source_status))
    app.add_handler(CommandHandler("backup", backup_cmd))
    app.add_handler(CommandHandler("livecheck", livecheck))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.post_init = set_commands  # runs inside the event loop after init
    print("Bot polling...")
    app.run_polling()

if __name__ == "__main__":
    main()
