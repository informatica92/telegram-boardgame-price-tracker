import datetime

from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater, CallbackContext, ConversationHandler, \
    CallbackQueryHandler
import os

from telegram_handler.telegram_handler import TelegramHandler


TOKEN = os.getenv("TOKEN")

INSERTING_DESIRED_PRICE_STATE = 1
EDIT_DESIRED_PRICE_STATE = 2
DELETE_WATCH_STATE = 3

telegram_handler = TelegramHandler()
telegram_handler.init_schema()


def start_command(update: Update, context: CallbackContext):
    """Send a message when the command /start is issued."""
    user = update.message.from_user
    user_name = user.name
    user_id = user.id
    telegram_handler.add_user(user_id, user_name)
    update.message.reply_text(f"START: {user.name} - {user.id}")


def help_command(update: Update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text("HELP")


def add_url_to_watch_list(update: Update, context: CallbackContext):
    user = update.message.from_user
    user_id = user.id
    url = context.user_data['url']
    desired_price = update.message.text
    telegram_handler.add_watch_for_user(user_id, url, desired_price)
    update.message.reply_text("ADDED")
    return ConversationHandler.END


def ask_for_desired_price(update: Update, context: CallbackContext):
    url = update.message.text
    context.user_data['url'] = url
    update.message.reply_text("Ok, which is your desired price for this product?")
    return INSERTING_DESIRED_PRICE_STATE


def ask_for_new_desired_price(update: Update, context: CallbackContext):
    url = update.message.text
    context.user_data['url'] = url
    update.message.reply_text("Ok, which is your desired price for this product?")
    return INSERTING_DESIRED_PRICE_STATE


def get_all_watched_urls_by_user(update: Update, context: CallbackContext):
    """Send a message when the command /start is issued."""
    user = update.message.from_user
    user_id = user.id
    watched_urls = telegram_handler.get_all_watched_urls_by_user(user_id)

    telegram_handler.list_products(context, watched_urls, user_id)


def repeated_watch(context: CallbackContext):
    print("scanning for watched urls")
    users = telegram_handler.get_all_users()

    for user_id in users:
        print(f"    user id {user_id}")
        watches = telegram_handler.get_all_watched_urls_by_user(user_id)
        telegram_handler.list_products(context, watches, user_id, only_below_desired_price=True, intro="WE FOUND THIS MATCH FOR YOU:\n")


def repeated_watch_command(update: Update, context: CallbackContext):
    repeated_watch(context)


def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    print(query.data)


# Create the Updater and pass it your bot's token.
# Make sure to set use_context=True to use the new context based callbacks
# Post version 12 this will no longer be necessary
updater = Updater(TOKEN, use_context=True)

# Get the dispatcher to register handlers
dp = updater.dispatcher

# on different commands - answer in Telegram
dp.add_handler(CommandHandler("start", start_command))
dp.add_handler(CommandHandler("help", help_command))
dp.add_handler(CommandHandler("list", get_all_watched_urls_by_user))
dp.add_handler(CallbackQueryHandler(button))
# dp.add_handler(CommandHandler("watch_all", repeated_watch_command))

conv_insert_new_watch_handler = ConversationHandler(
    entry_points=[MessageHandler(Filters.text, ask_for_desired_price)],
    states={INSERTING_DESIRED_PRICE_STATE: [MessageHandler(Filters.text, add_url_to_watch_list)]},
    fallbacks=[]
)

conv_inline_markup_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(button)],
    states={INSERTING_DESIRED_PRICE_STATE: [MessageHandler(Filters.text, add_url_to_watch_list)]},
    fallbacks=[]
)

# on non-command
dp.add_handler(conv_insert_new_watch_handler)

# Start the Bot
updater.start_polling()

j = updater.job_queue
j.run_repeating(repeated_watch, datetime.timedelta(hours=1))

# Run the bot until you press Ctrl-C or the process receives SIGINT,
# SIGTERM or SIGABRT. This should be used most of the time, since
# start_polling() is non-blocking and will stop the bot gracefully.
updater.idle()


# TODO: add "edit desired price" and "delete" option in /list
