from ibai_exceptions import ExistingAuctionException, AuctionException, CategoryException


class Category:
    def __init__(self, name):
        """Initialize a new category
        :param name:  name of the category
        """
        if len(name) < 1:
            raise Exception("Invalid Name")
        self.name = name
        self.auctions = []

    def add_auction(self, auction):
        """Add an auction to the category
        :param auction: Auction object to be added
        """
        if auction in self.auctions:
            raise AuctionException("Auction " + auction.name + " already exists")
        else:
            self.auctions.append(auction)

    def del_auction(self, auction):
        self.auctions.remove(auction)

    def search_auction(self, name):
        """
        Search for an auction in this category
        :param name: name of the auction
        :return: Auction object
        """
        for auction in self.auctions:
            if auction.name == name:
                return auction
        raise ExistingAuctionException("Auction not found")

    @staticmethod
    def search_category(cat_list, name):
        """Search for a category by name in the list
        :param cat_list: list of categories
        :param name: name of the category to match
        :return: Category object
        """
        name = name
        try:
            if name not in cat_list:
                raise CategoryException("Category not found")
            return cat_list[name]
        except KeyError, e:
            raise CategoryException(str(e))
