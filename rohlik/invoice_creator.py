import math

from typing import List

from rohlik.exceptions import TotalPriceError
from rohlik.email_manager import *
from rohlik.payers import Payers

from rohlik.groceries import Item, get_total, Groceries

MSG_KEYWORD = 'Potvrzení objednávky'
USER_ID = "me"
SENDER = "rohlik_invoice@gmail.com"
MESSAGE_KEYWORD = "from:zakaznici@rohlik.cz"
LINE = "\n____________________________________________________\n"


class Invoice:
    def __init__(self):
        self.email_service = EmailService(USER_ID, SENDER)
        self.groceries = Groceries.import_groceries()
        self.payers = Payers()

    def get_item_payer(self, item_name: str):
        if not (payer := self.payers.get_payer(self.groceries.get_payers_name(item_name))):
            payer = self.payers.create_items_payer(item_name)
        return payer

    def get_items_payers(self, message):
        items = Groceries.extract_groceries(message=message)
        for i, item in enumerate(items):
            payer = self.get_item_payer(item.name)
            item.payer = payer.name
            items[i] = item
            self.groceries.update(item)
        self.groceries.export()
        self.check_total_amount(message, items)
        return items

    def create_invoice(self, groceries: List[Item]):
        for item in groceries:
            self.payers.add_item_price(item.payer, item.price)
        return self.create_invoice_message(groceries)

    def create_invoice_message(self, items: List[Item]):
        msg = " \n".join(f"{item.payer}: {item.name} {item.price:.2f} Kč" for item in items)
        message = f"Thanks for being so awesome!{LINE}{msg}{LINE}{str(self.payers)}"
        print(message)
        return message

    @staticmethod
    def check_total_amount(message: str, order: List[Item]):
        total_price = get_total(message)
        if not math.isclose(total_price, calculated_price := sum(item.price for item in order), abs_tol=0.5):
            raise TotalPriceError(f"Total price {total_price} is not close to calculated price {calculated_price}")

    def create(self):
        email = self.email_service.get_message_with_keyword(MESSAGE_KEYWORD, MSG_KEYWORD, 0)

        for item in (order := self.get_items_payers(email)):
            self.payers.add_item_price(item.payer, item.price)
        message = self.create_invoice_message(order)

        emails = ", ".join([payer.email for payer in self.payers if payer.email])
        if input('Would you like to send an invoice? y/n\n') == 'y':
            self.email_service.send_message(emails, "Rohlik invoice", message)


if __name__ == '__main__':
    invoice = Invoice()
    invoice.create()
