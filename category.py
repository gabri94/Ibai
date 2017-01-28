class Category:
    def __init__(self, name):
        if len(name) < 1:
            raise Exception("Invalid Name")
        self.name = name
        self.auctions = []

    def add_auction(self, auction):
        if(self.search_auction(auction.name)):
            raise Exception("Auction " + auction.name + " already exists")
        self.auctions.append(auction)

    def search_auction(self, name):
        for auction in self.auctions:
            if auction.name.lower() == name.lower():
                return auction
        return False

    @staticmethod
    def search_category(cat_list, name):
        name = name.lower()
        c = cat_list[name]
        return c
