import psycopg2
import os
from telegram import ParseMode
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from price_tracker.shop_factory import ShopFactory


class TelegramHandler(object):
    def __init__(self):
        self.db_conn = os.getenv("DB_CONN")
        pass

    def get_connection(self):
        conn = psycopg2.connect(self.db_conn)
        return conn

    def init_schema(self):
        con = self.get_connection()
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS "user" (
                user_id INTEGER,
                name TEXT,
                CONSTRAINT user_PK PRIMARY KEY (user_id)
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS watch (
                user_id INTEGER,
                url TEXT,
                desired_price real,
                CONSTRAINT watch_PK PRIMARY KEY (user_id,url),
                CONSTRAINT watch_FK FOREIGN KEY (user_id) REFERENCES "user"(user_id)
            );
        """)
        con.commit()
        con.close()

    def add_user(self, user_id, user_name):
        con = self.get_connection()
        cur = con.cursor()
        cur.execute(f"SELECT user_id FROM public.user WHERE user_id = {user_id}")
        if len(cur.fetchall()) == 0:
            cur.execute(f"INSERT INTO public.user (user_id, name) VALUES ({user_id}, '{user_name}')")
            con.commit()
            con.close()

    def add_watch_for_user(self, user_id, url, desired_price):
        con = self.get_connection()
        cur = con.cursor()
        cur.execute(f"SELECT user_id, url FROM public.watch WHERE user_id = {user_id} and url = '{url}'")
        if len(cur.fetchall()) == 0:
            cur.execute(f"INSERT INTO watch (user_id, url, desired_price) VALUES ({user_id}, '{url}', {desired_price})")
            con.commit()
            con.close()

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
        failed_urls = sf.get_failed_urls()
        unhandled_urls = sf.get_unhandled_urls()
        if failed_urls:
            print("FAILED URLS:")
            print(failed_urls)
        if unhandled_urls:
            print("UNHANDLED URLS:")
            print(unhandled_urls)

    def get_all_watched_urls_by_user(self, user_id):
        con = self.get_connection()
        cur = con.cursor()
        cur.execute(f"SELECT url, desired_price FROM public.watch WHERE user_id = {user_id}")
        watched_urls = cur.fetchall()
        con.close()
        return watched_urls

    def get_all_users(self):
        con = self.get_connection()
        cur = con.cursor()
        cur.execute("SELECT DISTINCT user_id FROM public.watch")
        users = cur.fetchall()
        con.close()
        users = [user[0] for user in users]
        return users

