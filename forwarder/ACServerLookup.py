import requests

class ACServerLookup:

    def __init__(self, acserver, api_secret):
        self.acserver = acserver
        self.api_secret = api_secret

    def lookup_name(self, card_id):
        headers = { 'API-KEY' : self.api_secret }
        try:
            r = requests.get("%s/api/get_user_name/%s" % (self.acserver, card_id), headers=headers)
            result = r.json()
            if 'error' in r.json():
                print("Warning: Error returned from acserver")
                return ""
            return result['user_name']
        except ex:
            print("Got exception while trying to get name")
            return ""