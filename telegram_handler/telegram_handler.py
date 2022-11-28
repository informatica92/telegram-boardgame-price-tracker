import sqlite3

from telegram import ParseMode
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from price_tracker.shop_factory import ShopFactory


class TelegramHandler(object):
    def __init__(self):
        self.db_name = "watch.db"
        pass

    def init_schema(self):
        con = sqlite3.connect(self.db_name, check_same_thread=False)
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

    def add_user(self, user_id, user_name):
        con = sqlite3.connect(self.db_name, check_same_thread=False)
        if len(con.execute(f"SELECT user_id FROM user WHERE user_id = {user_id}").fetchall()) == 0:
            con.execute(f"INSERT INTO user (user_id, name) VALUES ({user_id}, '{user_name}')")
            con.commit()

    def add_watch_for_user(self, user_id, url, desired_price):
        con = sqlite3.connect(self.db_name, check_same_thread=False)
        if len(con.execute(
                f"SELECT user_id, url FROM watch WHERE user_id = {user_id} and url = '{url}'").fetchall()) == 0:
            con.execute(f"INSERT INTO watch (user_id, url, desired_price) VALUES ({user_id}, '{url}', {desired_price})")
            con.commit()

    @staticmethod
    def list_products(context, watched_urls_dict: dict, user_id, only_below_desired_price=False, intro=""):
        sf = ShopFactory(watched_urls_dict)
        product_list = sf.product_list
        for product in product_list:
            if (only_below_desired_price is True and product.difference < 0) or (only_below_desired_price is False):
                message = intro
                message += f"<b><a href='{product.url}'>{product.name}</a></b> {'🟩' if product.is_available else '🟥'}"
                message += f"\n🏷️{product.price.amount_text}{product.price.currency} "
                if product.discount > 0:
                    message += f"<s>{product.original_price.amount_text}{product.price.currency}</s> (-{product.discount:.0f}%)"
                if product.desired_price:
                    message += f"\n💡{product.desired_price}{product.price.currency} " \
                               f"({'+' if product.difference > 0 else ''}{product.difference:.2f}{product.price.currency}) " \
                               f"{'🥳' if product.difference < 0 else '🤬'}"
                keyboard = [
                    [
                        InlineKeyboardButton("edit desire price", callback_data=2),
                        InlineKeyboardButton("delete", callback_data=3),
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                context.bot.send_message(chat_id=user_id, text=message, parse_mode=ParseMode.HTML, reply_markup=reply_markup)

    def get_all_watched_urls_by_user(self, user_id):
        con = sqlite3.connect(self.db_name, check_same_thread=False)
        watched_urls = con.execute(f"SELECT url, desired_price FROM watch WHERE user_id = {user_id}").fetchall()
        return watched_urls

    def get_all_users(self):
        con = sqlite3.connect(self.db_name, check_same_thread=False)
        users = con.execute("SELECT DISTINCT user_id FROM watch").fetchall()
        users = [user[0] for user in users]
        return users

