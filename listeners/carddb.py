import json, time, os.path

class CardDB:
    def __init__(self, filename="/root/Doorbot/carddb.json"):
        self.filename = filename
        self.lastModified = time.ctime(os.path.getmtime(filename))
        self.db = json.load(open(filename, "r"))

    def nickForCard(self, card_serial):
        self.maybeRefresh()
        for entry in self.db:
            if card_serial in entry['cards']:
                return entry['nick']
        return None

    def maybeRefresh(self):
        timestamp = time.ctime(os.path.getmtime(self.filename))
        if timestamp > self.lastModified:
            print 'refreshing'
            self.lastModified = timestamp
            self.db = json.load(open(self.filename, "r"))
