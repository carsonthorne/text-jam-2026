from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Button, Static
from textual.containers import Vertical

from screens.game_screen import GameScreen
from screens.lobby_screen import LobbyScreen
from screens.identity_screen import IdentityScreen
from screens.join_session_screen import JoinSessionScreen
from local_identity import load_identity, clear_identity

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
            Button("Switch Player", id="switch_player"),
            Button("Quit", id="quit")
        )

    def on_mount(self):
        self.app.client.on_message = self.handle_message

        identity = load_identity()

        if identity:
            self.app.client.identity = identity
        else:
            self.app.push_screen(IdentityScreen())

    def handle_message(self, data):
        if data["type"] == "error":
            print(data["message"])

    def on_button_pressed(self, event: Button.Pressed):

        button_id = event.button.id

        if button_id == "quit":

            self.app.exit()

        elif button_id == "create":

            client = self.app.client
            identity = client.identity

            if not identity:
                self.app.push_screen(IdentityScreen())
                return

            client.connect(HOST, PORT)

            self.app.push_screen(LobbyScreen(client, identity))

            client.send({
                "type": "connect",
                "player_id": identity["player_id"],
                "session_id": None,
                "name": identity["name"]
            })
        
        elif button_id == "join":

            identity = self.app.client.identity

            if not identity:
                self.app.push_screen(IdentityScreen())
                return

            self.app.push_screen(JoinSessionScreen())

        elif button_id == "switch_player":

            clear_identity()

            self.app.client.identity = None

            self.app.push_screen(IdentityScreen())