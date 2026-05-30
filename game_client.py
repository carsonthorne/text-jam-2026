import socket
import threading
from network import send_json, receive_json
from message_types import CONNECT, DEBUG

class GameClient:

    def __init__(self):
        self.socket = None
        self.receive_thread = None
        self.running = False

        self.buffer = ""

        self.on_message = None

        self.identity = None


    def connect(self, host, port):

        if self.socket:
            self.close()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))

        self.buffer = ""

        self.running = True

        self.receive_thread = threading.Thread(
            target=self._receive_loop,
            daemon=True
        )
        self.receive_thread.start()


    def connect_to_session(
        self,
        host,
        port,
        identity,
        session_id=None,
        num_players=None
    ):

        self.connect(host, port)

        self.send({
            "type": CONNECT,
            "player_id": identity["player_id"],
            "session_id": session_id,
            "name": identity["name"],
            "num_players": num_players
        })


    def send(self, data):
        send_json(self.socket, data)


    def close(self):
        self.running = False
        if self.socket:
            self.socket.close()


    def _receive_loop(self):
        while self.running:
            try:
                data, self.buffer = receive_json(self.socket, self.buffer)

                if data is None:
                    break

                if self.on_message:

                    self.on_message(data)

            except Exception as e:
                self.app.log("Client receive error:", e)
                self.send({"type": DEBUG, "message": f"EXCEPTION: GAME_CLIENT.PY: {e}"})
                break

        self.running = False

    def dispatch_to_ui(self, app, callback, *args):

        app.call_from_thread(callback, *args)