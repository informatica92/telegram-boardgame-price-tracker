from price_parser import Price

from price_tracker.shop import Shop, Product


class MagicMerchant(Shop):
    URL = "https://magicmerchant.it/"

    def __init__(self):
        super(MagicMerchant, self).__init__(self.URL)

    def get_product_from_url(self, url: str) -> Product:
        soup = self.get_soup_object_from_url(url)

        tmp = soup.find("div", {"class": "col-sm-6 product_main"})
        name = tmp.find("h1").text
        price = Price.fromstring(tmp.find("p", {"class": "price_color"}).text)
        regular_price = tmp.find("p", {"class": "price_orig"})
        available = tmp.find("p", {"class": "outofstock availability verbose availability-message"}) is None
        if regular_price:
            regular_price = Price.fromstring(regular_price.text)
        product = Product(name, price, regular_price, available, url, self.name)
        return product
