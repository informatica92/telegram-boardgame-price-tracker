import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater, CallbackContext, ConversationHandler, \
    CallbackQueryHandler
import json
import os

from telegram_handler.telegram_handler import TelegramHandler


TOKEN = os.getenv("TOKEN")

INSERTING_DESIRED_PRICE_STATE = 1
CONFIRM_NEW_DESIRED_PRICE_STATE = 2
CONFIRM_DELETE_WATCH_STATE = 3

telegram_handler = TelegramHandler()
telegram_handler.init_schema()


def start_command(update: Update, _: CallbackContext):
    """Send a message when the command /start is issued."""
    user = update.message.from_user
    user_name = user.name
    user_id = user.id
    telegram_handler.add_user(user_id, user_name)
    update.message.reply_text(f"START: {user.name} - {user.id}")


def help_command(update: Update, _: CallbackContext):
    """Send a message when the command /help is issued."""
    update.message.reply_text("HELP")


def add_url_to_watch_list(update: Update, context: CallbackContext):
    user = update.message.from_user
    user_id = user.id
    url = context.user_data['url']
    desired_price = update.message.text
    telegram_handler.add_or_update_watch_for_user(user_id, url, desired_price)
    update.message.reply_text("Done!")
    return ConversationHandler.END


def ask_for_desired_price(update: Update, context: CallbackContext):
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
    intro = "WE FOUND THIS MATCH FOR YOU:\n"
    users = telegram_handler.get_all_users()

    for user_id in users:
        print(f"    user id {user_id}")
        watches = telegram_handler.get_all_watched_urls_by_user(user_id)
        telegram_handler.list_products(context, watches, user_id, only_below_desired_price=True, intro=intro)


def repeated_watch_command(_: Update, context: CallbackContext):
    repeated_watch(context)


def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    data = json.loads(query.data)
    watch_id = data['watch_id']
    watch = telegram_handler.get_watch(watch_id)
    user_id = watch[0]
    url = watch[1]
    current_desired_price = watch[2]
    if data['action'] == 'edit':
        context.user_data['url'] = url
        context.bot.send_message(
            chat_id=user_id,
            text=f"Which is your new desired price for this product? (current: {current_desired_price})"
        )
        return CONFIRM_NEW_DESIRED_PRICE_STATE
    if data['action'] == 'delete':
        keyboard = [
            [
                InlineKeyboardButton(
                    "yes",
                    callback_data=json.dumps({'watch_id': watch_id, 'action': 'confirm_delete'})
                ),
                InlineKeyboardButton(
                    "no",
                    callback_data=json.dumps({'watch_id': watch_id, 'action': 'abort_delete'})
                ),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(
            chat_id=user_id,
            text="Are you sure you want to delete this watch?",
            reply_markup=reply_markup
        )
        return ConversationHandler.END
    if data['action'] == 'confirm_delete':
        telegram_handler.delete_watch(watch_id)
        context.bot.send_message(chat_id=user_id, text="Done!")
    if data['action'] == 'abort_delete':
        pass


# Create the Updater and pass it your token.
# Make sure to set use_context=True to use the new context based callbacks
# Post version 12 this will no longer be necessary
updater = Updater(TOKEN, use_context=True)

# Get the dispatcher to register handlers
dp = updater.dispatcher

# on different commands - answer in Telegram
dp.add_handler(CommandHandler("start", start_command))
dp.add_handler(CommandHandler("help", help_command))
dp.add_handler(CommandHandler("list", get_all_watched_urls_by_user))
# dp.add_handler(CommandHandler("watch_all", repeated_watch_command))

conv_insert_new_watch_handler = ConversationHandler(
    entry_points=[
        MessageHandler(Filters.text, ask_for_desired_price),
        CallbackQueryHandler(button)
    ],
    states={
        INSERTING_DESIRED_PRICE_STATE: [MessageHandler(Filters.text, add_url_to_watch_list)],
        CONFIRM_NEW_DESIRED_PRICE_STATE: [MessageHandler(Filters.text, add_url_to_watch_list)]
    },
    fallbacks=[]
)

# conv_inline_markup_handler = ConversationHandler(
#     entry_points=[CallbackQueryHandler(button)],
#     states={CONFIRM_NEW_DESIRED_PRICE_STATE: [MessageHandler(Filters.text, add_url_to_watch_list)]},
#     fallbacks=[]
# )

# on non-command
dp.add_handler(conv_insert_new_watch_handler)
# dp.add_handler(conv_inline_markup_handler)

# Start the Bot
updater.start_polling()

j = updater.job_queue
j.run_repeating(repeated_watch, datetime.timedelta(hours=1))

# Run the bot until you press Ctrl-C or the process receives SIGINT,
# SIGTERM or SIGABRT. This should be used most of the time, since
# start_polling() is non-blocking and will stop the bot gracefully.
updater.idle()
