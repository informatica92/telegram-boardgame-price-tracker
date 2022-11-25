import difflib
from time import time

import pandas as pd

from price_tracker import shops


class ShopFactory(object):

    SHOPS = shops.all_my_base_classes

    def __init__(self, url_watch_list: dict):

        product_list = []
        handled_urls = []
        failed_url = {}
        start_time = time()
        for url, desired_price in url_watch_list.items():
            for shop in ShopFactory.SHOPS:
                try:
                    if str(url).startswith(shop.URL):
                        handled_urls.append(url)
                        product = shop().get_product_from_url(url)
                        product.desired_price = desired_price
                        product_list.append(product)
                except BaseException as ex:
                    failed_url[url] = ex
        self.duration = time() - start_time
        self.product_list = product_list
        self.unhandled_urls = list(set(url_watch_list) - set(handled_urls))
        self.failed_url = failed_url

    def get_duration(self, unit='second'):
        allowed_units = {
            'second': 1,
            'minutes': 60
        }
        if unit not in allowed_units:
            raise AttributeError(f"Unexpected unit: {unit} not in {allowed_units}")
        return self.duration/allowed_units[unit]

    def get_unhandled_urls(self):
        return self.unhandled_urls

    def get_failed_urls(self):
        return self.failed_url

    def get_dataframe(self, only_available=False, only_below_desired_price=False):
        if len(self.product_list) > 0:
            df = pd.DataFrame(self.product_list)
            df['price'] = df['price'].apply(lambda x: x.amount)
            df['original_price'] = df['original_price'].apply(lambda x: x.amount)
            df["discount"] = df["discount"].astype(int)
            df['name'] = df['name'].str.title()

            base_names = []
            for n in df['name']:
                matched = difflib.get_close_matches(n, base_names, cutoff=0.9)
                if len(matched) == 0:
                    base_names.append(n)

            df['name'] = df['name'].apply(lambda x: difflib.get_close_matches(x, base_names)[0])

            if only_available:
                df = df.query("is_available == True")

            if only_below_desired_price:
                df = df.query("price<desired_price")

            df = df.sort_values(by=['name', 'price'], ascending=[False, True]).reset_index(drop=True)
            return df
        else:
            return pd.DataFrame()

    def get_best(self, only_below_desired_price=False):
        df = self.get_dataframe(only_available=True, only_below_desired_price=only_below_desired_price)
        if len(df) > 0:
            df = df.sort_values(by=['name', 'price'], ascending=[False, True]).reset_index(drop=True)
            df_best = df.groupby("name").first().reset_index(drop=False)
            return df_best
        else:
            return pd.DataFrame
