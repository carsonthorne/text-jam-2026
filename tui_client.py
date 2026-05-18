from textual.app import App, ComposeResult
from textual.widgets import Static
from textual.events import Key
import socket
import threading
import json

from board_renderer import BoardRenderer

DIRECTION_KEYS = {
    "w": (0, -1),
    "e": (1, -1),
    "d": (1, 0),
    "x": (0, 1),
    "z": (-1, 1),
    "a": (-1, 0),
}

HOST = "127.0.0.1"
PORT = 5555

def send_json(client, data):

    message = json.dumps(data) + "\n"

    client.send(message.encode())

class ChineseCheckersApp(App):

    def __init__(self):

        super().__init__()

        self.renderer = BoardRenderer()

        self.board = {}

        self.cursor = (0, 0)

        self.selected_path = []

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.client.connect((HOST, PORT))

        self.player_id = None

        self.my_turn = False

    def compose(self) -> ComposeResult:

        self.board_widget = Static()

        yield self.board_widget

    def on_mount(self):

        self.refresh_board()

        receive_thread = threading.Thread(
            target=self.receive_messages,
            daemon=True
        )

        receive_thread.start()

    def receive_messages(self):

        buffer = ""

        while True:

            try:

                chunk = self.client.recv(1024).decode()

                if not chunk:
                    break

                buffer += chunk

                while "\n" in buffer:

                    line, buffer = buffer.split("\n", 1)

                    if not line:
                        continue

                    data = json.loads(line)

                    msg_type = data["type"]

                    if msg_type == "welcome":

                        self.player_id = data["player_id"]

                    elif msg_type == "game_state":

                        serialized_board = data["board"]

                        new_board = {}

                        for key, value in serialized_board.items():

                            q, r = map(int, key.split(","))

                            new_board[(q, r)] = value

                        current_player = data["current_player"]

                        # VERY IMPORTANT:
                        # update UI safely

                        self.call_from_thread(
                            self.update_game_state,
                            new_board,
                            current_player
                        )

                    elif msg_type == "error":

                        message = data["message"]

                        self.call_from_thread(
                            self.show_error,
                            message
                        )

            except Exception as e:

                print("Connection error:", e)

                break

    def update_game_state(self, new_board, current_player):

        self.board = new_board

        if self.cursor not in self.board:

            self.cursor = next(iter(self.board))

        self.my_turn = (
            current_player == self.player_id
        )

        self.refresh_board()

    def show_error(self, message):

        print("ERROR:", message)

    def refresh_board(self):

        board_str = self.renderer.build_board_string(
            self.board,
            self.cursor,
            self.selected_path
        )

        self.board_widget.update(board_str)

    def on_key(self, event: Key):

        if not self.my_turn:
            return

        key = event.key

        if key in DIRECTION_KEYS:

            direction = DIRECTION_KEYS[key]

            new_coord = (
                self.cursor[0] + direction[0],
                self.cursor[1] + direction[1]
            )

            if new_coord in self.board:

                self.cursor = new_coord

                self.refresh_board()

        elif key == "space":

            self.selected_path.append(self.cursor)

            self.refresh_board()

        elif key == "enter":

            if len(self.selected_path) >= 2:

                self.send_move()

                self.selected_path.clear()

                self.refresh_board()

    def send_move(self):

        send_json(self.client, {
            "type": "move",
            "path": self.selected_path
        })


if __name__ == "__main__":
    app = ChineseCheckersApp()
    app.run()