from price_tracker.shop_factory import ShopFactory

if __name__ == '__main__':
    url_watch_list = {
        # DUNGEONDICE
        "https://www.dungeondice.it/27300-happy-little-dinosaurs.html": 20,
        "https://www.dungeondice.it/28497-happy-little-dinosaurs-espansione-5-6-giocatori.html": 14,
        # BOTEGA LUDICA
        "https://bottegaludica.it/collections/newest-products/products/happy-little-dinosaurs": 20,
        "https://bottegaludica.it/collections/preordini/products/happy-little-dinosaurus-espansione-5-6-giocatori": 14,
        # MAGIC MERCHANT
        "https://magicmerchant.it/catalogue/happy-little-dinosaurs-60062/": 20,
        "https://magicmerchant.it/catalogue/happy-little-dinosaurs-espansione-5-6-giocatori-62664/": 15,
        # DADI E MATTONCINI
        "https://www.dadiemattoncini.it/giochi-da-tavolo/party-games/happy-little-dinosaurs.html": 20,
        # AMAZON
        "https://www.amazon.it/Asmodee-Little-Dinosaurs-Edizione-Italiano/dp/B09X4D4SS6": 20
    }

    sf = ShopFactory(url_watch_list)

    print(f"COMPLETED IN {sf.get_duration():.2f}s")
    print()

    print("ALL PRICES:")
    df = sf.get_dataframe()
    print(df.to_markdown())
    print()

    print("Unhandled URLs:")
    print(sf.get_unhandled_urls())
    print()

    print("Failed URLs:")
    print(sf.get_failed_urls())
    print()

    print("BEST PRICES:")
    df_best = sf.get_best()
    print(df_best.to_markdown())
    print()

    print("MATCHING DESIRED PRICES:")
    df_best = sf.get_best(only_below_desired_price=True)
    print(df_best.to_markdown())
    print()

    # TODO: add other shops (blazone shop, amazon, philbert...)
    # TODO: add scheduler
    # TODO: add caching (5min)
    # TODO: add alert system
