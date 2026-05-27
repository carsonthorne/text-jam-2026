import socket
import threading
from network import send_json, receive_json


class GameClient:
    def __init__(self):
        self.socket = None
        self.receive_thread = None
        self.running = False

        self.buffer = ""


        # callback hooks (screens will attach these)
        self.on_message = None

        self.identity = None

    # -----------
    # CONNECTION
    # -----------
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

    def send(self, data):
        send_json(self.socket, data)

    def close(self):
        self.running = False
        if self.socket:
            self.socket.close()

    # -------------
    # RECEIVE LOOP
    # -------------
    def _receive_loop(self):
        while self.running:
            try:
                data, self.buffer = receive_json(self.socket, self.buffer)

                if data is None:
                    break

                if self.on_message:
                    
                    self.on_message(data)

            except Exception as e:
                print("Client receive error:", e)
                self.send({"type": "debug", "message": f"exception inside game_client {e}"})
                break

        self.running = False