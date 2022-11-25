from dataclasses import dataclass

from price_parser import Price


@dataclass
class Product(object):
    name: str
    price: Price
    original_price: Price
    discount: float
    is_available: bool
    store: str
    url: str
    desired_price: float
    difference: float

    def __init__(self, name, price, original_price, is_available, url, store, desired_price=None):
        self.name = name
        self.price = price
        self.original_price = original_price if original_price and original_price.amount and original_price > price else price
        self.discount = self.calculate_discount()
        self.is_available = is_available
        self.url = url
        self.store = store
        self.desired_price = desired_price

    @property
    def difference(self):
        return self.desired_price-self.price.amount_float if self.desired_price else None

    def calculate_discount(self) -> float:
        discount = 0
        if self.original_price:
            discount = (self.original_price.amount - self.price.amount) / self.original_price.amount * 100
        return discount
