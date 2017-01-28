class Auction:
    def __init__(self, name, price):
        price = float(price)
        name = name.lower()
        if len(name) < 1:
            raise Exception("Invalid Name")
        if price <= 0:
            raise Exception("Invalid price value")
        self.name = name
        self.bids = []
        self.bids.insert(0, price)

    def bid(self, price):
        price = float(price)
        if price < self.bids[0]:
            raise Exception("Invalid bid")
        else:
            self.bids.insert(0, price)
