import re
import json

from typing import Optional

from rohlik import PATH_DATA
from rohlik.exceptions import TotalPriceError

PATH_GROCERIES = PATH_DATA / "grocery_list.json"
PATTERN_ITEM = r"\[Product\](.*\n?){1,3}\[(.*\n?.*)\].*\n.*?(\d+)\*\s(\d+,\d+)\sKč"
PATTERN_DISCOUNT = r"\+\s+(\d+,?\d+)\s+kreditů"
PATTERN_TIP = r"Spropitné pro kurýra.*?(\d+,\d+)\sKč"
PATTERN_DELIVERY_FEE = r"Doprava.*?(\d+,\d+)\sKč"
PATTERN_TOTAL_PRICE = r"Celkem.*?(\d+\s?\d+,\d+)\sKč"


def find_matches(text: str, pattern: str) -> list:
    return re.findall(pattern, text, re.MULTILINE)


def str_to_price(s: str) -> float:
    return float(s.replace(" ", "").replace(",", "."))


def get_discount(message):
    if matches := find_matches(message, PATTERN_DISCOUNT):
        return str_to_price(matches[0])
    return 0


def get_delivery_fee(message):
    if matches := find_matches(message, PATTERN_DELIVERY_FEE):
        return str_to_price(matches[0])
    return 0


def get_tip(message):
    if matches := find_matches(message, PATTERN_TIP):
        return str_to_price(matches[0])
    return 0


def get_total(message):
    if matches := find_matches(message, PATTERN_TOTAL_PRICE):
        return str_to_price(matches[0])
    raise TotalPriceError("Cannot parse total price from a message")


class Item:
    def __init__(self, name, price: Optional[float] = None, payer: Optional[str] = None):
        self.name = name
        self.price = price
        self.payer = payer

    def __str__(self):
        return f"name: {self.name}, price: {self.price}, payer: {self.payer}"

    def to_dict(self):
        return {"name": self.name, "payer": self.payer}

    @staticmethod
    def from_json(json_file):
        return Item(name=json_file["name"], payer=json_file["payer"], price=json_file.get("price"))


class Groceries(list):
    def __init__(self):
        super().__init__()

    def to_dict(self):
        return [item.to_dict() for item in self]

    def get_item(self, name: str):
        for item in self:
            if item.name == name:
                return item

    def update(self, new_item: Item):
        if any(item.name == new_item.name for item in self):
            for i, item in enumerate(self):
                if item.name == new_item.name:
                    self[i] = item
        else:
            self.append(new_item)

    def get_payers_name(self, item_name: str):
        if item := self.get_item(item_name):
            return item.payer

    def export(self):
        json_string = json.dumps(self.to_dict(), indent=2, ensure_ascii=False)
        with PATH_GROCERIES.open("w", encoding="utf-8") as f:
            f.write(json_string)

    @staticmethod
    def import_groceries():
        out = Groceries()
        if PATH_GROCERIES.exists():
            groceries = json.load(PATH_GROCERIES.open("rt"))
            for item in groceries:
                out.append(Item(name=item["name"], payer=item["payer"]))
        return out

    @staticmethod
    def extract_groceries(message: str):
        out = Groceries()
        for item in find_matches(message, PATTERN_ITEM):
            name = item[1].replace("\n", " ")
            price = int(item[2]) * float(item[3].replace(",", "."))
            out.append(Item(name=name, price=price))
        out.append(Item(name="Delivery", price=get_delivery_fee(message), payer="Shared"))
        out.append(Item(name="Discount", price=-get_discount(message), payer="Shared"))
        out.append(Item(name="Tip", price=get_tip(message), payer="Shared"))
        return out

    def __str__(self):
        return "\n".join(str(item) for item in self)
