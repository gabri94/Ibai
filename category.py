from ibai_exceptions import ExistingAuctionException, AuctionException, CategoryException


class Category:
    def __init__(self, name):
        if len(name) < 1:
            raise Exception("Invalid Name")
        self.name = name
        self.auctions = []

    def add_auction(self, auction):
        try:
            if(self.search_auction(auction.name)):
                raise AuctionException("Auction " + auction.name + " already exists")
        except ExistingAuctionException:
            self.auctions.append(auction)

    def search_auction(self, name):
        for auction in self.auctions:
            if auction.name.lower() == name.lower():
                return auction
        raise ExistingAuctionException("Auction not found")

    @staticmethod
    def search_category(cat_list, name):
        name = name.lower()
        try:
            c = cat_list[name]
            if not c:
                raise CategoryException("Category not found")
            return c
        except KeyError, e:
            raise CategoryException(str(e))
