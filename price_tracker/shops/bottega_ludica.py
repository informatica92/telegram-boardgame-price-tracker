from price_parser import Price

from price_tracker.shop import Shop, Product


class BottegaLudica(Shop):
    URL = "https://bottegaludica.it/"

    def __init__(self):
        super(BottegaLudica, self).__init__(self.URL)

    def get_product_from_url(self, url: str) -> Product:
        soup = self.get_soup_object_from_url(url)

        name = soup.find("h1", {"class": "prd-block_title"}).text
        price = Price.fromstring(soup.find("span", {"class": "prd-block_price--actual"}).text)
        regular_price = soup.find("span", {"class": "prd-block_price--old"})
        available = soup.find("div", {"class": "prd-availability"}).find("span").text.strip() != "Non disponibile"
        if regular_price:
            regular_price = Price.fromstring(regular_price.text)
        product = Product(name, price, regular_price, available, url, self.name)
        return product
