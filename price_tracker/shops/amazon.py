from price_parser import Price

from price_tracker.shop import Shop, Product


class Amazon(Shop):
    URL = "https://www.amazon.it/"

    def __init__(self):
        super(Amazon, self).__init__(self.URL)

    def get_product_from_url(self, url: str) -> Product:
        soup = self.get_soup_object_from_url(url)

        name = soup.find("span", {"id": "productTitle"}).text
        price = Price.fromstring(
            f'{soup.find("span", {"class": "a-price-whole"}).text}{soup.find("span", {"class": "a-price-fraction"}).text}{soup.find("span", {"class": "a-price-symbol"}).text}'
        )
        regular_price = soup.find("span", {"class": "a-price a-text-price a-size-base"})
        available = True
        if regular_price:
            regular_price = Price.fromstring(regular_price.text)
        product = Product(name, price, regular_price, available, url, self.name)
        return product
