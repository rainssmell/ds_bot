def calculate_price(package, addons):
    base_prices = {
        "3h": 14900,
        "5h": 19900,
        "8h": 24900
    }

    addons_price = 0

    if "mics" in addons:
        addons_price += 990
    if "light" in addons:
        addons_price += 2900
    if "extra" in addons:
        addons_price += 3900

    return base_prices[package] + addons_price
