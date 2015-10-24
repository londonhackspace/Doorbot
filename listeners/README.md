These scripts react to broadcast messages sent out by doorbots (UDP broadcast, back doorbot port 50001, front doorbot port 50002).

Scripts running on hamming as of 14 September 2015:

* doorbot-glados.py
* doorbot-boarded.py
* doorbot-irccat.py (frond and back)
* doorbot-lastseen.py (front and back)

# doorbot-boarded.py

Connects to a boarded instance running on hamming:8020, submits a message via a GET request that gets displayed on a led matrix board.

Two instances listening on different ports sending the same message.

# doorbot-lastseen.py

Listens for messages, writes an entry via pickle to a local file, for consumption by other scripts.

Two instances, one for the front, and one for the back door, using the same file.

# doorbot-irccat.py

Reads and refreshes the database from the pickled file produced by `lastseen` and does the following:

* When a bell is rang, sends a message to the channel.
* When a known card is presented, sends a message with a nickname to the channel including when the user was last seen.
* When an unknown card is presented, sends a messages to the channel.
