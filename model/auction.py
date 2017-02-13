from ibai_exceptions import AuctionException, UserException, PriceException, BidException


class Auction:
    def __init__(self, name, price, owner):
        """ Initalize the Auction object
        :param name: name of the product
        :param price: base price
        :param owner: owner User object
        """
        price = float(price)
        name = name.lower()
        if len(name) < 1:
            raise AuctionException("Invalid Name")
        if price <= 0:
            raise PriceException("Invalid price value")
        self.owner = owner
        self.name = name
        self.users = []
        self.users.append(owner)
        self.bids = []
        self.closed = False
        bid = {
            "price": price,
            "user": owner
        }
        self.bids.insert(0, bid)

    def bid(self, price, user):
        """ Place a bid on this auction
        :param price: value of the bid
        :param user: user making the bid
        """
        price = float(price)
        if self.closed:
            raise AuctionException("Closed Auction")
        if price < self.bids[0]["price"]:
            raise BidException("Invalid bid")
        if self.bids[0]["user"] == user:
            raise UserException("Multiple bid")
        bid = {
            "price": price,
            "user": user
        }
        self.bids.insert(0, bid)
        self.users.append(user)

    def unbid(self, user):
        """ Remove our bid only if it's the highest
        :param user: user removing the bid
        """
        if self.closed:
            raise AuctionException("Closed Auction")
        if self.bids[0]["user"] != user:
            raise UserException("User not match")
        self.bids.remove(0)
        self.bids.pop()

    def winner(self):
        """ Get the winner """
        winner = self.bids[0]
        return self.bids[0]["user"]

    def close(self, user):
        """ Close the auction and notify the subscribed users
        :param user: user closing the auction
        """
        if self.closed:
            raise AuctionException("Closed Auction")
        if len(self.bids) <= 1:
            raise AuctionException("No winner")
        if self.owner != user:
            raise UserException("User not allowed")
        self.closed = True
        self.__notify_all(1, "Asta chiusa")
        self.winner().notify(2, "Hai vinto")

    def __notify_all(self, code, msg):
        """
        Notify all the users
        :param code: code of the notification
        :param msg: message of the notification
        """
        for user in self.users:
            user.notify(code, msg)