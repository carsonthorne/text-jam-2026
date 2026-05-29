import time

class Player:

    def __init__(self, player_id, player_number, name, session_id):
        
        self.player_id = player_id
        self.player_number = player_number
        self.name = name
        self.session_id = session_id

        self.connection = None

        self.connected = False

        self.last_seen = time.time()


    def attach_connection(self, conn):

        self.connection = conn
        self.connected = True

        self.last_seen = time.time()


    def disconnect(self):

        self.connection = None
        self.connected = False

        self.last_seen = time.time()