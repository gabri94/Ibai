from ibai_exceptions import AuctionException, UserException, PriceException, BidException
from utils import debug_print

class Auction:
    def __init__(self, name, price, owner):
        """ Initalize the Auction object
        :param name: name of the product
        :param price: base price
        :param owner: owner User object
        """
        price = float(price)
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
        print price
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
        if self.winner()!=self.owner:
            self.winner().notify(3, "La tua offerta e' stata superata")
        self.bids.insert(0, bid)
        debug_print(self.name)
        debug_print(self.bids)
        debug_print(self.users)
        if user not in self.users:
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
        print "Chiuso"
        self.__notify_all(1, "Asta chiusa")
        self.winner().notify(2, "Hai vinto")

    def __notify_all(self, code, msg):
        """
        Notify all the users
        :param code: code of the notification
        :param msg: message of the notification
        """
        print "Notifico tutti"
        for user in self.users:
            print "Notifico: " + user.name
            user.notify(code, msg)