from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater

import os


TOKEN = os.getenv("TOKEN")


def start_command(update: Update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text("START")


def help_command(update: Update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text("HELP")


def fallback_action(update: Update, context):
    update.message.reply_text("FALLBACK")


# Create the Updater and pass it your bot's token.
# Make sure to set use_context=True to use the new context based callbacks
# Post version 12 this will no longer be necessary
updater = Updater(TOKEN, use_context=True)

# Get the dispatcher to register handlers
dp = updater.dispatcher

# on different commands - answer in Telegram
dp.add_handler(CommandHandler("start", start_command))
dp.add_handler(CommandHandler("help", help_command))

# on non-command
dp.add_handler(MessageHandler(Filters.text, fallback_action))

# Start the Bot
updater.start_polling()

# Run the bot until you press Ctrl-C or the process receives SIGINT,
# SIGTERM or SIGABRT. This should be used most of the time, since
# start_polling() is non-blocking and will stop the bot gracefully.
updater.idle()
