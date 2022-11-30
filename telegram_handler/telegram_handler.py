import json

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
                watch_id SERIAL,
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

    def add_or_update_watch_for_user(self, user_id, url, desired_price):
        con = self.get_connection()
        cur = con.cursor()
        cur.execute(f"SELECT user_id, url FROM public.watch WHERE user_id = {user_id} and url = '{url}'")
        if len(cur.fetchall()) == 0:
            cur.execute(f"INSERT INTO watch (user_id, url, desired_price) VALUES ({user_id}, '{url}', {desired_price})")
        else:
            cur.execute(f"UPDATE watch SET desired_price = {desired_price} WHERE user_id = {user_id} and url = '{url}'")
        con.commit()
        con.close()

    def get_watch(self, watch_id):
        con = self.get_connection()
        cur = con.cursor()
        cur.execute(f"SELECT user_id, url, desired_price FROM public.watch WHERE watch_id = {watch_id}")
        return cur.fetchone()

    def delete_watch(self, watch_id):
        con = self.get_connection()
        cur = con.cursor()
        cur.execute(f"DELETE FROM public.watch WHERE watch_id = {watch_id}")
        rows_deleted = cur.rowcount
        con.commit()
        con.close()
        return rows_deleted

    @staticmethod
    def list_products(context, watched_urls: list, user_id, only_below_desired_price=False, intro=""):
        sf = ShopFactory(watched_urls)
        product_list = sf.product_list
        for prod in product_list:
            if (only_below_desired_price is True and prod.difference < 0) or (only_below_desired_price is False):
                message = intro
                message += f"<b><a href='{prod.url}'>{prod.name}</a></b> {'🟩' if prod.is_available else '🟥'}"
                message += f"\n🏷️{prod.price.amount_text}{prod.price.currency} "
                if prod.discount > 0:
                    message += f"<s>{prod.original_price.amount_text}{prod.price.currency}</s> " \
                               f"(-{prod.discount:.0f}%)"
                if prod.desired_price:
                    message += f"\n💡{prod.desired_price}{prod.price.currency} " \
                               f"({'+' if prod.difference > 0 else ''}{prod.difference:.2f}{prod.price.currency}) " \
                               f"{'🥳' if prod.difference < 0 else '🤬'}"
                keyboard = [
                    [
                        InlineKeyboardButton(
                            "✒edit desire price",
                            callback_data=json.dumps({'watch_id': prod.watch_id, 'action': 'edit'})
                        ),
                        InlineKeyboardButton(
                            "❌delete",
                            callback_data=json.dumps({'watch_id': prod.watch_id, 'action': 'delete'})
                        ),
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                context.bot.send_message(
                    chat_id=user_id,
                    text=message,
                    parse_mode=ParseMode.HTML,
                    reply_markup=reply_markup
                )
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
        cur.execute(f"SELECT watch_id, url, desired_price FROM public.watch WHERE user_id = {user_id}")
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
