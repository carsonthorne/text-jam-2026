from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Button, Static
from textual.containers import Vertical

from screens.game_screen import GameScreen

HOST = "127.0.0.1"
PORT = 5555

class MainMenuScreen(Screen):

    def __init__(self):
        super().__init__()

    def compose(self) -> ComposeResult:

        yield Vertical(
            Static("[bold cyan]Chinese Checkers[/]"),
            Button("Create Session", id="create"),
            Button("Join Session", id="join"),
            Button("Rules", id="rules"),
            Button("Controls", id="controls"),
            Button("Quit", id="quit")
        )

    def on_mount(self):
        self.app.client.on_message = self.handle_message

    def handle_message(self, data):
        if data["type"] == "error":
            print(data["message"])

    def on_button_pressed(self, event: Button.Pressed):

        button_id = event.button.id

        if button_id == "quit":

            self.app.exit()

        else:

            if button_id == "create":

                client = self.app.client
                client.connect(HOST, PORT)

                identity = {
                    "player_id": "test-player",
                    "session_id": None,
                    "name": "Carson"
                }

                client.send({
                    "type": "connect",
                    "player_id": identity["player_id"],
                    "session_id": None,
                    "name": identity["name"]
                })

                self.app.push_screen(GameScreen(self.app.client, identity))