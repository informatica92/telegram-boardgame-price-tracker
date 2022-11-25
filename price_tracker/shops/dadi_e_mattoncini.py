from price_parser import Price

from price_tracker.shop import Shop, Product


class DadiEMattoncini(Shop):
    URL = "https://www.dadiemattoncini.it"

    def __init__(self):
        super(DadiEMattoncini, self).__init__(self.URL)

    def get_product_from_url(self, url: str) -> Product:
        soup = self.get_soup_object_from_url(url)

        name = soup.find("h3", {"class": "product-title"}).text
        price = Price.fromstring(soup.find("span", {"class": "product-price"}).text)
        regular_price = soup.find("span", {"class": "old-price"})
        available = soup.find("p", {"class": "out-of-stock"}) is None
        if regular_price:
            regular_price = Price.fromstring(regular_price.text)
        product = Product(name, price, regular_price, available, url, self.name)
        return product
