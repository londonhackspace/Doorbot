from MQTTDoorbotListener import MQTTDoorbotListener
import time
import datetime
import concurrent.futures
import urllib.request
import requests

pool = concurrent.futures.ProcessPoolExecutor()

def doIt(url):
    try:
        requests.get(url)
    except Exception as e:
                print("Error connecting to %s: %s" % (url, str(e)))

class SignsDoorbotListener(MQTTDoorbotListener):

    def on_card(self, card_id, name, door, gladosfile):
        if not door.getboolean('announce', True):
            print("Ignorning non-annoucing door %s" % (door['name'],))
            return
        if name == 'Inspector Sands':
            msg = "%s reported to %s" % (name, door['name'])
        else:
            msg = "%s opened %s" % (name, door['name'])

        self.send_message(msg)

    def on_bell(self, door):
        today = datetime.date.today()
        m, d = today.month, today.day
        if (m, d) >= (12, 24) and (m, d) <= (12, 31):
            dingdong = 'DING DONG MERRILY ON HIGH, DOOR BELL!'
        else:
            dingdong = 'DING DONG, DOOR BELL!'
        self.send_message("%s (%s)" % (dingdong, door['name']))

    def send_message(self, message):
        print('%s %s' % (time.strftime('%Y-%m-%d %H:%M:%S'), message))
        for board in self.config['default']['boards'].split(','):
            board = self.config[board.strip()]
            url = "http://%s:%d/%s?restoreAfter=%d" % \
                        (board['host'], int(board['port']), urllib.request.quote(message), int(board['restoreafter']))
            print("Connecting to %s" %  (url,))

            
            pool.submit(doIt, url)


if __name__ == '__main__':
    dbl = SignsDoorbotListener()
    dbl.run()