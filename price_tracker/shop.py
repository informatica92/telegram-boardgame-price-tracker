from datetime import timedelta

import requests_cache
from bs4 import BeautifulSoup

from price_tracker.product import Product

CACHE_NAME = "requests.cache"
CACHE_DURATION_MINUTES = 5


class Shop(object):
    def __init__(self, base_url: str, cache_minutes=None):
        self.base_url = base_url
        self.cache_minutes = timedelta(minutes=cache_minutes or CACHE_DURATION_MINUTES)
        self.name = self.__class__.__name__

    def get_soup_object_from_url(self, url: str):
        session = requests_cache.CachedSession(CACHE_NAME, expire_after=self.cache_minutes)
        html = session.get(url).content
        soup = BeautifulSoup(html, "lxml")
        return soup

    def get_product_from_url(self, url: str) -> Product:
        pass

    def get_products_from_url_list(self, url_list):
        return [self.get_product_from_url(url) for url in url_list]


