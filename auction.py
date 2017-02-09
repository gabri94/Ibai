from ibai_exceptions import AuctionException, UserException


class Auction:
    def __init__(self, name, price, owner):
        price = float(price)
        name = name.lower()
        if len(name) < 1:
            raise AuctionException("Invalid Name")
        if price <= 0:
            raise Exception("Invalid price value")
        self.owner = owner
        self.name = name
        self.users = []
        self.bids = []
        bid = {
            "price": price,
            "user": owner
        }
        self.bids.insert(0, bid)

    def bid(self, price, user):
        price = float(price)
        if price < self.bids[0]["price"]:
            raise AuctionException("Invalid bid")
        if self.bids[0]["user"] == user:
            raise AuctionException("Invalid bid")
        bid = {
            "price": price,
            "user": user
        }
        self.bids.insert(0, bid)
        self.users.append(user)

    def unbid(self, user):
        if self.bids[0]["user"] != user:
            raise UserException("User not match")
        self.bids.remove()
        self.bids.pop()

    def winner(self):
        if len(self.bids) <= 1:
            raise Exception("No winner")
        self.notify_all(1, "The winner is")
        return self.bids[0]["user"]

    def close(self, user):
        if self.owner != user:
            raise Exception("User not allowed")
        self.notify_all(1, "Asta chiusa")
        self.winner().notiy(2, "Hai vinto")

    def notify_all(self, code, msg):
        for user in self.users:
            user.notify(code, msg)
