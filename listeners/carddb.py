import json

class CardDB:
    def __init__(self, filename="carddb.json"):
        f = open(filename, "r")
        self.db = json.load(f)

    def nickForCard(self, card_serial):
        for entry in self.db:
            if card_serial in entry['cards']:
                return entry['nick']
        return None
