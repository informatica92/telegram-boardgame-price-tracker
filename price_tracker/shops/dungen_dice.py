from price_parser import Price

from price_tracker.shop import Shop, Product


class DungeonDice(Shop):
    URL = "https://www.dungeondice.it/"

    def __init__(self):
        super(DungeonDice, self).__init__(self.URL)

    def get_product_from_url(self, url: str) -> Product:
        soup = self.get_soup_object_from_url(url)

        name = soup.find("h1", itemprop="name").text
        price = Price.fromstring(soup.find("div", itemprop="price").text)
        regular_price = soup.find("span", {"class": "regular-price"})
        available = soup.find("div", {"class": "add"}).find("span").text != "Prodotto non disponibile"
        if regular_price:
            regular_price = Price.fromstring(regular_price.text)
        product = Product(name, price, regular_price, available, url, self.name)
        return product
