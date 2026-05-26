from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Button, Static
from textual.containers import Vertical

import socket

from local_identity import load_identity
from network import send_json
from screens.game_screen import GameScreen

HOST = "127.0.0.1"
PORT = 5555

class MainMenuScreen(Screen):

    def compose(self) -> ComposeResult:

        yield Vertical(
            Static("[bold cyan]Chinese Checkers[/]"),
            Button("Create Session", id="create"),
            Button("Join Session", id="join"),
            Button("Rules", id="rules"),
            Button("Controls", id="controls"),
            Button("Quit", id="quit")
        )

    def on_button_pressed(self, event: Button.Pressed):

        button_id = event.button.id

        if button_id == "quit":

            self.app.exit()

        else:

            if button_id == "create":

                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # client.settimeout(5)
                client.settimeout(None)
                client.connect((HOST, PORT))

                # identity = load_identity(force_new=True)

                identity = {
                    "player_id": "test-player",
                    "session_id": None,
                    "name": "Carson"
                }

                send_json(client, {
                    "type": "connect",
                    "player_id": identity["player_id"],
                    "session_id": None,
                    "name": identity["name"]
                })

                self.app.push_screen(
                    GameScreen(client, identity)
                )