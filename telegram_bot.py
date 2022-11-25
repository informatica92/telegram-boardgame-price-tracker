from telegram import Update, ParseMode
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater, CallbackContext, ConversationHandler
from price_tracker.shop_factory import ShopFactory
import os

import sqlite3


TOKEN = os.getenv("TOKEN")

INSERTING_DESIRED_PRICE_STATE = 1

con = sqlite3.connect("watch.db", check_same_thread=False)
con.execute("""
    CREATE TABLE IF NOT EXISTS "user" (
        user_id INTEGER,
        name TEXT,
        CONSTRAINT user_PK PRIMARY KEY (user_id)
    );
""")
con.execute("""
    CREATE TABLE IF NOT EXISTS watch (
        user_id INTEGER,
        url TEXT,
        desired_price NUMERIC,
        CONSTRAINT watch_PK PRIMARY KEY (user_id,url),
        CONSTRAINT watch_FK FOREIGN KEY (user_id) REFERENCES "user"(user_id)
    );
""")
con.commit()
con.close()


def start_command(update: Update, context: CallbackContext):
    """Send a message when the command /start is issued."""
    user = update.message.from_user
    user_name = user.name
    user_id = user.id
    con = sqlite3.connect("watch.db", check_same_thread=False)
    if len(con.execute(f"SELECT user_id FROM user WHERE user_id = {user_id}").fetchall()) == 0:
        con.execute(f"INSERT INTO user (user_id, name) VALUES ({user_id}, '{user_name}')")
        con.commit()
    update.message.reply_text(f"START: {user.name} - {user.id}")


def help_command(update: Update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text("HELP")


def add_url_to_watch_list(update: Update, context: CallbackContext):
    user = update.message.from_user
    user_id = user.id
    con = sqlite3.connect("watch.db", check_same_thread=False)
    url = context.user_data['url']
    desired_price = update.message.text
    if len(con.execute(f"SELECT user_id, url FROM watch WHERE user_id = {user_id} and url = '{url}'").fetchall()) == 0:
        con.execute(f"INSERT INTO watch (user_id, url, desired_price) VALUES ({user_id}, '{url}', {desired_price})")
        con.commit()
    update.message.reply_text("FALLBACK")


def ask_for_desired_price(update: Update, context: CallbackContext):
    url = update.message.text
    context.user_data['url'] = url
    update.message.reply_text("Ok, which is your desired price for this product?")
    return INSERTING_DESIRED_PRICE_STATE


def get_all_watched_urls(update: Update, context: CallbackContext):
    """Send a message when the command /start is issued."""
    user = update.message.from_user
    user_id = user.id
    con = sqlite3.connect("watch.db", check_same_thread=False)
    watched_urls = con.execute(f"SELECT url, desired_price FROM watch WHERE user_id = {user_id}").fetchall()

    watched_urls_dict = {}
    for watch in watched_urls:
        watched_urls_dict[watch[0]] = watch[1]
    sf = ShopFactory(watched_urls_dict)
    product_list = sf.product_list
    for product in product_list:
        message = ""
        message += f"<b><a href='{product.url}'>{product.name}</a></b> available: {product.is_available}"
        if product.discount > 0:
            message += f"\n{product.price.amount_text}{product.price.currency} " \
                       f"<s>{product.original_price.amount_text}{product.price.currency}</s> " \
                       f"({product.discount:.0f}%)"
        else:
            message += f"\n{product.price.amount_text}"
        update.message.reply_text(message, parse_mode=ParseMode.HTML)

    # update.message.reply_text(message, parse_mode=ParseMode.HTML)


# Create the Updater and pass it your bot's token.
# Make sure to set use_context=True to use the new context based callbacks
# Post version 12 this will no longer be necessary
updater = Updater(TOKEN, use_context=True)

# Get the dispatcher to register handlers
dp = updater.dispatcher

# on different commands - answer in Telegram
dp.add_handler(CommandHandler("start", start_command))
dp.add_handler(CommandHandler("help", help_command))
dp.add_handler(CommandHandler("list", get_all_watched_urls))

conv_username_handler = ConversationHandler(
    entry_points=[MessageHandler(Filters.text, ask_for_desired_price)],
    states={INSERTING_DESIRED_PRICE_STATE: [MessageHandler(Filters.text, add_url_to_watch_list)]},
    fallbacks=[]
)

# on non-command
dp.add_handler(conv_username_handler)

# Start the Bot
updater.start_polling()

# Run the bot until you press Ctrl-C or the process receives SIGINT,
# SIGTERM or SIGABRT. This should be used most of the time, since
# start_polling() is non-blocking and will stop the bot gracefully.
updater.idle()
