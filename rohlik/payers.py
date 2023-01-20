import json

from typing import Optional

from rohlik import PATH_DATA

PATH_PAYERS = PATH_DATA / 'payers.json'


class Payer:
    def __init__(self, name, email: Optional[str] = None, money_paid: int = 0):
        self.name = name
        self.email = email
        self.money_paid = money_paid

    def to_dict(self):
        return {"name": self.name, "email": self.email}

    def __str__(self):
        return f"{self.name}: {self.money_paid:.2f} Kč"


class Payers(list):
    def __init__(self):
        super().__init__()
        self.import_payers()

    def get_payer(self, name):
        return next((payer for payer in self if payer.name == name), None)

    def is_payer_valid(self, name: str):
        return name and any(payer.name == name for payer in self)

    def create_items_payer(self, item_name: str):
        payer_name = None
        while not self.is_payer_valid(payer_name):
            payer_name = input(f"Who pays for {item_name}?\n")
        return self.get_payer(payer_name)

    def add_shared_price(self, item_price):
        price = item_price / (len(self) - 1)
        for payer in self:
            if payer.name != "Shared":
                payer.money_paid += price

    def add_item_price(self, payer_name, item_price):
        price = item_price if payer_name != "Shared" else item_price / (len(self) - 1)
        for payer in self:
            if payer.name == payer_name != "Shared" or payer_name == "Shared" != payer.name:
                payer.money_paid += price

    def to_dict(self):
        return [payer.to_dict() for payer in self]

    def create_payers(self):
        print("Creating a list of people.")
        while True:
            name = input("Enter a name. Type 'x' to exit.\n")
            if name == 'x':
                break
            elif name in self:
                print(f"{name} is already in the list. Try adjusting the name.\n")
            else:
                email = input(f"Enter an email for user {name}\n")
                self.append(Payer(name=name, email=email))
        if len(self) > 1:
            self.append(Payer(name='Shared'))
        with open(PATH_PAYERS, "w") as outfile:
            json.dump(self.to_dict(), outfile, indent=2)

    def import_payers(self):
        if PATH_PAYERS.exists():
            payers = json.load(PATH_PAYERS.open("rt"))
            for payer in payers:
                self.append(Payer(name=payer["name"], email=payer["email"]))
        else:
            self.create_payers()

    def __str__(self):
        return ", ".join(str(payer) for payer in self if payer.name != "Shared")
