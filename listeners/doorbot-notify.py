#!/usr/bin/env python
import select, socket, pynotify

if __name__ == "__main__":

    if not pynotify.init("icon-summary-body"):
        sys.exit(1)

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('<broadcast>', 50000))
    s.setblocking(0)

    while True:

        result = select.select([s],[],[])
        payload = result[0][0].recv(1024)
        (event, card, name) = payload.split("\n")

        title = message = ''

        if (event == 'RFID' and name):
            title   = "Door opened"
            message = "%s opened the hackspace door." % name

        elif (event == 'RFID' and not name):
            title   = "ALERT"
            message = "An unknown RFID card was used on the hackspace door."

        elif (event == 'BELL'):
            title   = "BING BONG!"
            message = "Someone pressed the hackspace doorbell."

        if title and message:
            pynotify.Notification(title, message).show()
